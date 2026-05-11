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
# Gemini fallback reader
# ─────────────────────────────────────────────
class GeminiReader:
    """
    Záložní čtečka využívající Gemini 2.0 Flash.
    Používá se pouze pokud PERO OCR není dostupné nebo selže.
    """

    def __init__(self):
        from google import genai
        if 'GEMINI_API_KEY' not in os.environ:
            raise ValueError("GEMINI_API_KEY není nastaven.")
        self.client = genai.Client()
        self.model_name = 'gemini-2.0-flash'

    def query_image(self, image_path: str, prompt: str) -> str:
        try:
            img = Image.open(image_path)
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[img, prompt]
            )
            return response.text
        except Exception as e:
            return f"Error: {e}"


# ─────────────────────────────────────────────
# Hybridní AIReader (hlavní třída pro skripty)
# ─────────────────────────────────────────────
class AIReader:
    """
    Hybridní čtečka:
      1. Pokusí se extrahovat text přes PERO OCR (specializovaný na historické rukopisy).
      2. Hledá příjmení Dias (a varianty) pomocí regex v extrahovaném textu.
      3. Pokud PERO OCR selže nebo API klíč chybí, použije Gemini jako fallback.

    Tato třída zachovává stejné rozhraní jako původní AIReader,
    takže ostatní skripty (deep_search_ivanovice.py apod.) nevyžadují změny.
    """

    MODE_HYBRID = 'hybrid'   # PERO primárně, Gemini jako fallback
    MODE_PERO   = 'pero'     # pouze PERO OCR + regex
    MODE_GEMINI = 'gemini'   # pouze Gemini (původní chování)

    def __init__(self, mode: str = MODE_HYBRID):
        self.mode = mode
        self.pero = PEROReader()
        self._gemini = None  # lazy init

        if mode == self.MODE_HYBRID:
            if self.pero.available:
                print("[AIReader] Režim: HYBRID (PERO OCR primárně, Gemini fallback)")
            else:
                print("[AIReader] PERO_API_KEY nenalezen → fallback na Gemini")
        elif mode == self.MODE_PERO:
            if not self.pero.available:
                raise ValueError("PERO_API_KEY není nastaven, režim 'pero' nelze použít.")
            print("[AIReader] Režim: PERO OCR only")
        else:
            print("[AIReader] Režim: Gemini only")

    @property
    def gemini(self) -> GeminiReader:
        if self._gemini is None:
            self._gemini = GeminiReader()
        return self._gemini

    # ── Hlavní metoda ──────────────────────────────────────────────────────
    def query_image(self, image_path: str, prompt: str) -> str:
        """
        Prohledá obrázek a vrátí:
          - text nalezených shod (pokud příjmení existuje)
          - "NENALEZENO" pokud nic není
          - "Error: ..." pokud nastala chyba
        """
        if self.mode == self.MODE_GEMINI:
            return self.gemini.query_image(image_path, prompt)

        # ── 1. Pokus přes PERO OCR ─────────────────────────────────────────
        if self.pero.available:
            print(f"  [PERO] Zpracovávám {Path(image_path).name}...")
            extracted_text = self.pero.extract_text(image_path)

            if extracted_text:
                return self._search_in_text(extracted_text, image_path)
            else:
                print(f"  [PERO] Prázdný výsledek, zkouším Gemini fallback...")

        # ── 2. Gemini fallback ─────────────────────────────────────────────
        if self.mode == self.MODE_PERO:
            return "Error: PERO OCR selhalo a Gemini fallback je zakázán (mode=pero)"

        print(f"  [Gemini] Analyzuji {Path(image_path).name}...")
        return self.gemini.query_image(image_path, prompt)

    # ── Pomocné metody ─────────────────────────────────────────────────────
    def _search_in_text(self, text: str, image_path: str) -> str:
        """Hledá příjmení v OCR textu pomocí regex."""
        matches = COMBINED_PATTERN.findall(text)
        if not matches:
            return "NENALEZENO"

        # Vrátí kontext: řádky obsahující shodu
        found_lines = []
        for line in text.splitlines():
            if COMBINED_PATTERN.search(line):
                found_lines.append(line.strip())

        summary = f"[PERO OCR nalezl] Příjmení: {set(matches)}\n"
        summary += "\n".join(found_lines[:10])  # max 10 řádků
        return summary

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
