import os
import re
import time
import json
import requests
from pathlib import Path
from PIL import Image

# ─────────────────────────────────────────────
# Target surnames to search for (regex)
# ─────────────────────────────────────────────
SURNAME_PATTERNS = [
    r'\bDias?\b',      # Dias, Dia
    r'\bDiaz\b',
    r'\bDius\b',
    r'\bDyas?\b',      # Dyas, Dya (fonetické varianty)
    r'\bDiáš\b',
]
COMBINED_PATTERN = re.compile('|'.join(SURNAME_PATTERNS), re.IGNORECASE)


# ─────────────────────────────────────────────
# PERO OCR Web API client
# ─────────────────────────────────────────────
PERO_API_URL = "https://pero-ocr.fit.vutbr.cz/api"
PERO_POLL_INTERVAL = 5   # sekund mezi dotazy na stav
PERO_MAX_WAIT = 300      # maximálně 5 minut čekání


class PEROReader:
    """
    Využívá PERO OCR REST API (pero-ocr.fit.vutbr.cz) pro rozpoznání
    textu z naskenovaných historických matrik.

    Ke spuštění potřebuje API klíč (PERO_API_KEY v .env).
    Pokud klíč chybí, vrátí None a systém přepne na Gemini fallback.
    """

    def __init__(self):
        self.api_key = os.environ.get('PERO_API_KEY')
        self.engine = os.environ.get('PERO_ENGINE', 'CzechHandwriting')
        self.available = self.api_key is not None

    def _headers(self):
        return {
            'api-key': self.api_key,
        }

    def extract_text(self, image_path: str) -> str | None:
        """
        Pošle obrázek na PERO OCR API a vrátí rozpoznaný text.
        Vrátí None pokud API není dostupné nebo nastala chyba.
        """
        if not self.available:
            return None

        try:
            # 1. Odeslání souboru
            with open(image_path, 'rb') as f:
                files = {'file': (Path(image_path).name, f, 'image/jpeg')}
                data = {'engine': self.engine}
                resp = requests.post(
                    f"{PERO_API_URL}/post_processing_request",
                    headers=self._headers(),
                    files=files,
                    data=data,
                    timeout=30,
                )

            if resp.status_code != 200:
                print(f"  [PERO] Upload failed: HTTP {resp.status_code} — {resp.text[:200]}")
                return None

            job_info = resp.json()
            request_id = job_info.get('request_id') or job_info.get('id')
            if not request_id:
                print(f"  [PERO] No request_id in response: {job_info}")
                return None

            # 2. Polling dokud není hotovo
            waited = 0
            while waited < PERO_MAX_WAIT:
                time.sleep(PERO_POLL_INTERVAL)
                waited += PERO_POLL_INTERVAL

                status_resp = requests.get(
                    f"{PERO_API_URL}/get_processing_status/{request_id}",
                    headers=self._headers(),
                    timeout=15,
                )
                if status_resp.status_code != 200:
                    continue

                status_data = status_resp.json()
                state = status_data.get('state', '').upper()

                if state in ('DONE', 'PROCESSED', 'FINISHED'):
                    break
                elif state in ('FAILED', 'ERROR'):
                    print(f"  [PERO] Processing failed for {image_path}")
                    return None
                # jinak čekáme dál

            else:
                print(f"  [PERO] Timeout waiting for {image_path}")
                return None

            # 3. Stažení výsledku (plain text)
            result_resp = requests.get(
                f"{PERO_API_URL}/download_results/{request_id}",
                headers=self._headers(),
                timeout=15,
            )
            if result_resp.status_code != 200:
                print(f"  [PERO] Download failed: HTTP {result_resp.status_code}")
                return None

            # Výsledek může být ZIP nebo JSON
            content_type = result_resp.headers.get('content-type', '')
            if 'application/json' in content_type:
                data = result_resp.json()
                # Zkusíme různé klíče
                text = data.get('text') or data.get('transcription') or data.get('content', '')
            else:
                text = result_resp.text

            return text.strip() if text else None

        except Exception as e:
            print(f"  [PERO] Exception: {e}")
            return None


# ─────────────────────────────────────────────
# Apple Local Reader (Entity Linking)
# ─────────────────────────────────────────────
class AppleLocalReader:
    """
    Lokální OpenAI-kompatibilní klient připojující se na localhost:11434.
    Očekává model `apple-foundationmodel`.
    Slouží primárně k Entity Linkingu - bere surový text (např. z Transkribusu)
    a porovnává ho s předem načteným rodokmenem (family tree).
    """
    def __init__(self):
        self.base_url = "http://localhost:11434/v1"
        self.model = "gemma2:2b"
        self.available = True
        
        # Načtení rodokmenu pomocí nového parseru
        self.family_tree = ""
        tree_path = Path(__file__).parent.parent.parent / "dias_family_tree.md"
        try:
            from mza_search.family_tree import FamilyTreeManager
            mgr = FamilyTreeManager(str(tree_path))
            self.family_tree = mgr.get_context_string()
        except Exception as e:
            print(f"[AppleLocalReader] Nelze načíst rodokmen přes parser: {e}")

    def analyze_text(self, text: str) -> str:
        if not text.strip():
            return "NENALEZENO"
            
        system_prompt = (
            "Jsi expert na genealogii a čtení historických matrik. "
            "Zde je ověřený rodokmen rodiny Dias a záchytné body (např. profese mlynář, lokace Zlobice č.p. 15, Ivanovice na Hané, apod.):\n\n"
            f"{self.family_tree}\n\n"
            "DŮLEŽITÉ: Při vyhledávání pečlivě kontroluj i jména manželek nebo manželů (pokud jsou uvedeni), protože pomáhají potvrdit shodu (např. při sňatku).\n\n"
            "ÚKOL:\n"
            "Níže je surový text extrahovaný z historické matriky pomocí OCR (obsahuje chyby čtení a starou němčinu/češtinu).\n"
            "Najdi jakoukoliv potenciální shodu s osobami z rodokmenu, nebo obecně s příjmením Dias/Dyas/Dijas a profesí mlynář v daných lokacích.\n"
            "Pokud najdeš shodu, vypiš jméno osoby z rodokmenu, u které shodu vidíš, a zdůvodnění proč (např. sedí manželka, sedí lokace).\n"
            "Pokud žádnou spojitost nevidíš, vrať POUZE slovo 'NENALEZENO'."
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Surový text z matriky k analýze:\n{text}"}
        ]
        
        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.2
                },
                timeout=120
            )
            if resp.status_code == 200:
                answer = resp.json()["choices"][0]["message"]["content"]
                if "NENALEZENO" in answer.upper() and len(answer) < 50:
                    return "NENALEZENO"
                return answer.strip()
            else:
                print(f"[AppleLocalReader] API Error {resp.status_code}: {resp.text}")
                return "Error: Local API Failed"
        except Exception as e:
            print(f"[AppleLocalReader] Chyba volání: {e}")
            return "Error: Connection Failed"


# ─────────────────────────────────────────────
# Local Copilot CLI reader
# ─────────────────────────────────────────────
class CopilotReader:
    """
    Využívá lokálního GitHub Copilot CLI pro analýzu obrázků.
    Bez API limitů a úplně místní.
    """

    def __init__(self):
        import subprocess
        self.available = True
        try:
            result = subprocess.run(['copilot', '--version'], capture_output=True, timeout=5)
            if result.returncode != 0:
                self.available = False
                print("[CopilotReader] Copilot CLI není dostupný")
        except Exception as e:
            self.available = False
            print(f"[CopilotReader] Error checking copilot: {e}")

    def query_image(self, image_path: str, prompt: str) -> str:
        """
        Pošle prompt a obrázek Copilotovi pomocí CLI s --attachment.
        """
        if not self.available:
            return "Error: Copilot CLI not available"
        
        try:
            import subprocess
            
            # Zavoláme Copilota s obrázkem jako attachment
            result = subprocess.run(
                ['copilot', 
                 '--prompt', prompt,
                 '--attachment', image_path,
                 '--allow-all'
                ],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error: {result.stderr[:200]}"
                
        except Exception as e:
            return f"Error: {e}"


# ─────────────────────────────────────────────
# Gemini fallback reader
# ─────────────────────────────────────────────
class GeminiReader:
    """
    Záložní čtečka využívající Gemini 2.5 Flash s integrovaným rodokmenem.
    Používá se pouze pokud PERO OCR není dostupné nebo selže.
    """

    def __init__(self):
        import google.genai
        if 'GEMINI_API_KEY' not in os.environ and 'GOOGLE_API_KEY' not in os.environ:
            raise ValueError("GEMINI_API_KEY nebo GOOGLE_API_KEY není nastaven.")
        self.client = google.genai.Client()
        self.model_name = 'gemini-3.5-flash-lite'
        
        # Načtení rodokmenu
        self.family_tree = ""
        tree_path = Path(__file__).parent.parent.parent / "dias_family_tree.md"
        try:
            from mza_search.family_tree import FamilyTreeManager
            mgr = FamilyTreeManager(str(tree_path))
            self.family_tree = mgr.get_context_string()
        except Exception as e:
            print(f"[GeminiReader] Nelze načíst rodokmen přes parser: {e}")

    def query_image(self, image_path: str, prompt: str) -> str:
        try:
            img = Image.open(image_path)
            # Optimalizace velikosti pro Gemini (max 4096 px)
            max_size = 4096
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            system_prompt = (
                "Jsi expert na genealogii a čtení historických matrik (17.-19. století) psaných kurentem a starou němčinou/češtinou.\n"
                "Zde je ověřený rodokmen rodiny Dias a záchytné body:\n\n"
                f"{self.family_tree}\n\n"
                "DŮLEŽITÉ: Při vyhledávání pečlivě kontroluj i jména manželek nebo manželů (pokud jsou uvedeni), protože pomáhají potvrdit shodu.\n\n"
                "ÚKOL:\n"
                "Přečti rukopis na přiloženém obrázku.\n"
                "Najdi jakoukoliv potenciální shodu s osobami z rodokmenu, nebo obecně s příjmením Dias/Dyas/Dijas a profesí mlynář v daných lokacích.\n"
                "Pokud najdeš shodu, vypiš jméno osoby z rodokmenu, u které shodu vidíš, a zdůvodnění proč, spolu s přepisem záznamu.\n"
                "Pokud žádnou spojitost nevidíš, vrať POUZE slovo 'NENALEZENO'."
            )
            
            import concurrent.futures
            def do_call():
                return self.client.models.generate_content(
                    model=self.model_name,
                    contents=[system_prompt, img]
                )
            
            pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            future = pool.submit(do_call)
            try:
                response = future.result(timeout=300)
                pool.shutdown(wait=False)
            except concurrent.futures.TimeoutError:
                pool.shutdown(wait=False, cancel_futures=True)
                return "Error: Gemini API Timeout (300s)"
            
            answer = response.text
            if "NENALEZENO" in answer.upper() and len(answer) < 50:
                return "NENALEZENO"
            return answer.strip()
        except Exception as e:
            return f"Error: {e}"

# ─────────────────────────────────────────────
# Transkribus API Reader
# ─────────────────────────────────────────────
class TranskribusReader:
    """
    Konzumuje Transkribus REST API.
    Nahrává jednotlivé obrázky do výchozí sbírky uživatele.
    """
    def __init__(self):
        self.email = os.environ.get('TRANSKRIBUS_EMAIL')
        self.password = os.environ.get('TRANSKRIBUS_PASSWORD')
        # Defaultujeme na model Old Czech Handwriting (with spaces)
        self.model_id = os.environ.get('TRANSKRIBUS_MODEL_ID', '341425') 
        self.col_id = os.environ.get('TRANSKRIBUS_COLLECTION_ID')
        
        self.base_url = "https://transkribus.eu/TrpServer/rest"
        self.available = bool(self.email and self.password)
        self.api = None
        self.session_token = None

    def _login(self) -> bool:
        if self.api is not None:
            return True
            
        try:
            from transkribus_rest_api import transkribus_rest_api
            from transkribus_rest_api.types import UploadPage
            print("  [Transkribus] Přihlašování k API (transkribus-rest-api)...")
            # Pro použití jako běžný objekt musíme vyvolat kontext manažer ručně, nebo jej spravovat přes with
            # Kvůli jednoduchosti se přihlásíme pomocí čistých requests pro získání JSESSIONID, 
            # ale použijeme i oficiální balíček
            self._ctx = transkribus_rest_api(self.email, self.password)
            self.api = self._ctx.__enter__()
            self.session_token = self.api.session_id.session_id
            
            # Pokud nemáme ID sbírky, vezmeme tu první (uživatel má defaultní sbírku po registraci)
            if not self.col_id:
                cols_resp = self.api.collections.list()
                if 'trpCollection' in cols_resp and cols_resp['trpCollection']:
                    self.col_id = cols_resp['trpCollection'][0]['colId']
                    print(f"  [Transkribus] Zvolena sbírka (Collection ID): {self.col_id}")
            return True
        except Exception as e:
            print(f"  [Transkribus] Chyba přihlášení: {e}")
            self.api = None
            return False

    def extract_text(self, image_path: str) -> str | None:
        """Nahraje obrázek do nového dokumentu, počká na zpracování a vrátí text"""
        if not self.available or not self._login():
            return None
            
        try:
            from transkribus_rest_api.types import UploadPage
            import xml.etree.ElementTree as ET
            import hashlib
            
            cookies = {'JSESSIONID': self.session_token}
            img_path = Path(image_path)
            img_name = img_path.name
            
            # 1. Vytvoření nového dokumentu a nahrání přes transkribus_rest_api
            print(f"  [Transkribus] Vytvářím dokument a nahrávám obrázek {img_name}...")
            # Spočítáme MD5
            md5_hash = hashlib.md5(img_path.read_bytes()).hexdigest()
            page = UploadPage(image=img_path, page_xml=None, page_nr=1, image_md5=md5_hash)
            
            doc_id = self.api.upload_document(int(self.col_id), f"MZA_Search_{img_name}", [page])
            print(f"  [Transkribus] Dokument nahrán úspěšně. (DocID: {doc_id})")
            
            # Nyní potřebujeme získat ID stránky, pro spuštění HTR
            # Dokument se zpracovává na serveru, proto zkusíme počkat
            import time
            page_id = None
            for wait_attempt in range(12):
                fulldoc_resp = requests.get(f"{self.base_url}/collections/{self.col_id}/{doc_id}/fulldoc", cookies=cookies)
                if fulldoc_resp.status_code == 200:
                    try:
                        page_id = fulldoc_resp.json()['pageList']['pages'][0]['pageId']
                        break
                    except (KeyError, IndexError):
                        pass
                print(f"  [Transkribus] Čekám na dostupnost dokumentu {doc_id} (pokus {wait_attempt+1}/12)...")
                time.sleep(5)
                
            if not page_id:
                print(f"  [Transkribus] Nelze získat pageId pro dokument {doc_id}.")
                return None
            
            # 3. Spuštění rozpoznávání (HTR)
            print(f"  [Transkribus] Spouštím model (ID: {self.model_id})...")
            payload = {"docId": doc_id, "pageList": {"pages": [{"pageId": page_id}]}}
            htr_url = f"{self.base_url}/pylaia/{self.col_id}/{self.model_id}/recognition?id={doc_id}&pages=1"
            htr_resp = requests.post(htr_url, cookies=cookies, json=payload)
            
            if htr_resp.status_code == 404:
                htr_url = f"{self.base_url}/recognition/{self.col_id}/{self.model_id}/htrCITlab?id={doc_id}&pages=1"
                htr_resp = requests.post(htr_url, cookies=cookies, json=payload)
                
            if htr_resp.status_code != 200:
                print(f"  [Transkribus] Nelze spustit model: {htr_resp.text}")
                return None
                
            try:
                js = htr_resp.json()
                if isinstance(js, list):
                    job_id = js[0].get('jobId', js[0])
                elif isinstance(js, dict):
                    job_id = js.get('jobId')
                else:
                    job_id = js
            except:
                import xml.etree.ElementTree as ET
                try:
                    root = ET.fromstring(htr_resp.text)
                    job_id = root.findtext(".//jobId")
                except:
                    job_id = None
                    
            if not job_id:
                print(f"  [Transkribus] Nelze vyčíst jobId: {htr_resp.text}")
                return None
            
            # 4. Polling stavu úlohy
            print("  [Transkribus] Čekám na dokončení (záleží na vytížení cloudu)...")
            for _ in range(60): # Max 5 minut čekání (60 x 5s)
                time.sleep(5)
                job_resp = requests.get(f"{self.base_url}/jobs/{job_id}", cookies=cookies)
                if job_resp.status_code == 200:
                    state = job_resp.json()['state']
                    if state == "FINISHED":
                        break
                    elif state in ["FAILED", "CANCELED"]:
                        print(f"  [Transkribus] Chyba úlohy na serveru (stav: {state}).")
                        return None
            else:
                print("  [Transkribus] Vypršel čas (Timeout) při čekání na server.")
                return None
            
            # 5. Získání textu
            print("  [Transkribus] Stahuji a parsuji výsledek...")
            fulldoc_resp = requests.get(f"{self.base_url}/collections/{self.col_id}/{doc_id}/fulldoc", cookies=cookies)
            if fulldoc_resp.status_code != 200:
                return None
                
            # Zjistíme URL PAGE XML souboru s transkripcí
            transcripts = fulldoc_resp.json()['pageList']['pages'][0].get('tsList', {}).get('transcripts', [])
            if not transcripts:
                print("  [Transkribus] Žádný text nebyl vrácen.")
                return None
                
            page_xml_url = transcripts[0]['url']
            xml_resp = requests.get(page_xml_url, cookies=cookies)
            
            # PAGE XML Parser: Hledáme uzly <Unicode> které obsahují rozpoznaný text řádku
            root = ET.fromstring(xml_resp.content)
            text_lines = []
            
            # Hledání s ohledem na ignorování jmenných prostorů (namespace)
            for elem in root.iter():
                if elem.tag.endswith('Unicode') and elem.text:
                    text_lines.append(elem.text.strip())

            final_text = "\n".join(text_lines)
            return final_text
            
        except Exception as e:
            print(f"  [Transkribus] Neočekávaná chyba: {e}")
            return None



# ─────────────────────────────────────────────
# Hybridní AIReader (hlavní třída pro skripty)
# ─────────────────────────────────────────────
class AIReader:
    """
    Hybridní čtečka:
      1. 'hybrid' - Zkusí Transkribus, pak Copilot, VUT API, nakonec Gemini.
      2. 'transkribus' - Pouze Transkribus.
      3. 'pero' - Pouze VUT API.
      4. 'gemini' - Pouze Gemini.
    """

    MODE_HYBRID      = 'hybrid'
    MODE_TRANSKRIBUS = 'transkribus'
    MODE_PERO        = 'pero'
    MODE_GEMINI      = 'gemini'

    def __init__(self, mode: str = MODE_TRANSKRIBUS):
        self.mode = mode
        self.apple = AppleLocalReader()
        self.transkribus = TranskribusReader()
        self.gemini = None

        if mode == self.MODE_TRANSKRIBUS:
            if self.transkribus.available:
                print(f"[AIReader] Režim: TRANSKRIBUS (Model ID: {self.transkribus.model_id}) + APPLE LOCAL LINKER")
            else:
                print("[AIReader] Transkribus chybí.")
        elif mode == self.MODE_GEMINI:
            self.gemini = GeminiReader()
            print("[AIReader] Režim: GEMINI 2.5 FLASH")
        else:
            print("[AIReader] Pouze Apple Local Linker")

    # ── Hlavní metoda ──────────────────────────────────────────────────────
    def query_image(self, image_path: str, prompt: str) -> str:
        """
        Prohledá obrázek a vrátí:
          - text nalezených shod (pokud příjmení existuje)
          - "NENALEZENO" pokud nic není
          - "Error: ..." pokud nastala chyba
        """
        if self.mode == self.MODE_GEMINI:
            print(f"  [Gemini] Zpracovávám obrázek {Path(image_path).name} pomocí Vision API...")
            return self.gemini.query_image(image_path, prompt)

        if not self.transkribus.available:
            return "Error: Transkribus is not available"
            
        print(f"  [Transkribus] Zpracovávám {Path(image_path).name} přes cloudové API...")
        extracted_text = self.transkribus.extract_text(image_path)
        if extracted_text:
            return self._search_in_text(extracted_text, image_path)
        else:
            print("  [Transkribus] Prázdný výsledek.")
            return "Error: Transkribus vrátil prázdný výsledek."

    # ── Pomocné metody ─────────────────────────────────────────────────────
    def _search_in_text(self, text: str, image_path: str) -> str:
        """Použije AppleLocalReader k nalezení spojitostí."""
        print(f"  [Apple] Analyzuji získaný text (délka: {len(text)} znaků)...")
        result = self.apple.analyze_text(text)
        
        # Můžeme také vypsat, pokud Transkribus nalezl 'Dias' natvrdo
        matches = COMBINED_PATTERN.findall(text)
        if matches:
            print(f"  [Regex Fallback] Ve zdrojovém textu byl nelezen řetězec: {set(matches)}")
            
        return result

    # ── Kompatibilní metoda pro cli.py ────────────────────────────────────
    def search_book_directory(self, directory_path: str, query: str, scan_list=None):
        """
        Prohledá všechny obrázky v adresáři.
        Zachovává původní rozhraní (generator yielding (filename, result)).
        """
        dir_path = Path(directory_path)
        if not dir_path.is_dir():
            raise FileNotFoundError(f"Adresář {directory_path} nenalezen.")

        images = sorted([
            f for f in dir_path.iterdir()
            if f.is_file() and f.suffix.lower() in ('.jpg', '.jpeg', '.png')
        ])

        if scan_list:
            filtered = []
            for img in images:
                try:
                    num = int(img.stem.split('_')[-1])
                    if num in scan_list:
                        filtered.append(img)
                except ValueError:
                    pass
            images = filtered

        if not images:
            yield None, "Žádné obrázky k analýze."
            return

        gemini_prompt = (
            f"Prohledej tento historický matriční záznam a odpověz na dotaz: '{query}'. "
            "Najdeš-li odpovídající osobu nebo událost, vypiš z dokumentu dohledatelné detaily."
        )

        for img_path in images:
            yield img_path.name, self.query_image(str(img_path), gemini_prompt)
