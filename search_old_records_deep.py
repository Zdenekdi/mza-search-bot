import os, sys, time, concurrent.futures
from PIL import Image
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from mza_search.client import MZAClient
from mza_search.scanner import MZAScanner
import google.genai

if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                k, v = line.split('=', 1)
                os.environ[k] = v

client = MZAClient()
scanner = MZAScanner(client)
genai_client = google.genai.Client()

def search_book(book_id, start_scan, end_scan, prompt, output_csv):
    csv_file = open(output_csv, "a", encoding="utf-8")
    for scan_idx in range(start_scan, end_scan + 1):
        print(f"Downloading scan {scan_idx}/{end_scan} of book {book_id}...")
        try:
            img_path = scanner.download_scan(book_id, scan_idx, f"book_{book_id}_scan_{scan_idx}.jpg")
        except Exception as e:
            print(f"Error downloading scan {scan_idx}: {e}")
            continue
            
        for attempt in range(5):
            try:
                print(f"Sending scan {scan_idx} to AI...")
                img = Image.open(img_path)
                max_size = 4096
                if max(img.size) > max_size:
                    ratio = max_size / max(img.size)
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    
                def do_call():
                    return genai_client.models.generate_content(
                        model='gemini-3.5-flash-lite',
                        contents=[prompt, img]
                    )
                    
                pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
                future = pool.submit(do_call)
                response = future.result(timeout=120)
                pool.shutdown(wait=False)
                
                ans = response.text.strip()
                
                if "NENALEZENO" not in ans.upper() or len(ans) > 50:
                    print(f"!!! FOUND SOMETHING ON SCAN {scan_idx} !!!")
                    csv_file.write(f'{book_id},{scan_idx},"{ans.replace(chr(34), chr(34)+chr(34))}"\n')
                    csv_file.flush()
                else:
                    print(f"Scan {scan_idx}: NENALEZENO")
                break
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower() or "503" in str(e):
                    print(f"Quota limit hit ({e}), sleeping...")
                    time.sleep(60)
                else:
                    print(f"Error AI: {e}")
                    time.sleep(5)

prompt_1353 = """
Jsi genealog. Prohlížíš matriku narozených (křtů) z let 1632-1685 z Ivanovic na Hané.
Hledáme KŘEST dítěte jménem JAN (Joannes) s příjmením DIAS (Dyas / Dijas / Dijn / Deig). Dítě by mělo být pokřtěno někdy kolem roku 1660. 
Otec dítěte by se mohl jmenovat Thomas (Tomáš) nebo Jiří (Georgius) Dias.

ÚKOL:
Pečlivě přečti všechny záznamy na stránce. Pokud najdeš křest dítěte, u kterého se objevuje příjmení Dias/Dyas/Dijas, PŘEPIŠ HO CELÝ (datum, jméno, otec, matka, kmotři).
Hledej i svatby, pokud je to společná matrika: sňatek otce Thomase nebo Jiřího s příjmením Dias.
Pokud nic nenajdeš, vrať POUZE slovo 'NENALEZENO'.
"""

prompt_1354 = """
Jsi genealog. Prohlížíš matriku narozených (křtů) z let 1686-1708.
Hledáme KŘEST dítěte jménem VÁCLAV (Wenzel / Wenceslaus) s příjmením DIAS (Dyas / Dijas). 
Otec dítěte by se měl jmenovat JAN (Joannes) Dias.

ÚKOL:
Pečlivě přečti všechny záznamy. Pokud najdeš křest jakéhokoliv dítěte Václava s příjmením Dias, nebo jakékoliv jiné dítě otce Jana Diase, PŘEPIŠ CELÝ ZÁZNAM.
Pokud nic nenajdeš, vrať POUZE slovo 'NENALEZENO'.
"""

import sys
if len(sys.argv) > 1 and sys.argv[1] == '1353':
    search_book("1353", 1, 226, prompt_1353, "nalezy_1353_nejstarsi.csv")
elif len(sys.argv) > 1 and sys.argv[1] == '1354':
    search_book("1354", 1, 236, prompt_1354, "nalezy_1354_narozeni_vaclava.csv")
