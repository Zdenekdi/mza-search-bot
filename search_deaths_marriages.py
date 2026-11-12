import os, sys, time, concurrent.futures
from PIL import Image
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from mza_search.client import MZAClient
from mza_search.scanner import MZAScanner
import google.genai
import csv

from dotenv import load_dotenv
load_dotenv()  # klíč ber z .env, ne z kódu
client = MZAClient()
scanner = MZAScanner(client)
genai_client = google.genai.Client()

def search_book(book_id, start_scan, end_scan, prompt, output_csv):
    results = []
    for scan_idx in range(start_scan, end_scan + 1):
        print(f"[{book_id}] Scan {scan_idx}/{end_scan}...")
        try:
            img_path = scanner.download_scan(book_id, scan_idx, f"book_{book_id}_scan_{scan_idx}.jpg")
        except Exception as e:
            print(f"Error downloading {scan_idx}: {e}")
            continue
            
        img = Image.open(img_path)
        # downsize a bit to save quota
        img.thumbnail((2000, 2000))
        
        for attempt in range(3):
            try:
                res = genai_client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=[prompt, img]
                )
                txt = res.text.strip()
                if txt and txt != "NENALEZENO":
                    print(f"!!! NALEZENO na str. {scan_idx} !!!\n{txt[:200]}")
                    results.append([scan_idx, txt])
                break
            except Exception as e:
                if "429" in str(e):
                    print("Quota... wait 15s")
                    time.sleep(15)
                else:
                    print(f"API err: {e}")
                    break
        time.sleep(1)
        
    with open(output_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for row in results:
            writer.writerow(row)

# Kniha 1353 (1632-1685) - Mortui/Copulati
# Svatba Tomáše a Mariny mohla být před 1664 (narození Jana). 
# Hledáme sňatky (Copulati) a úmrtí (Defuncti).
prompt_1353 = """
Hledej v této matrice sňatky (Copulati) nebo úmrtí (Defuncti).
Hledaná jména: Thomas Dijn / Dyas / Dias, Marina (manželka).
Případně Joannes Dijn (Jan st. narozen 1664).
Vypiš přesný datum, jména a text, pokud tam jsou.
Pokud tam nejsou, napiš jen NENALEZENO.
"""

# Kniha 1354 (1686-1708) - Mortui/Copulati
# Svatba Jana st. s Alžbětou (před 1694).
# Úmrtí Tomáše (po 1664, zřejmě do 1700).
prompt_1354 = """
Hledej v této matrice sňatky (Copulati) nebo úmrtí (Defuncti).
Hledaná jména: Joannes Dijn / Dyas / Dias, Elisabeth (manželka) - svatba.
Thomas Dijn / Dyas - úmrtí.
Vypiš přesný datum, jména a text, pokud tam jsou.
Pokud tam nejsou, napiš jen NENALEZENO.
"""

print("Starting scan 1353 for Thomas/Marina")
# V knize 1353 jsou sňatky a úmrtí obvykle v zadní části, zkusíme skeny 150-250
search_book("10141", 150, 210, prompt_1353, "nalezy_svatby_umrti_1353.csv")

print("Starting scan 1354 for Joannes/Elisabeth/Thomas")
# V knize 1354, zkusíme skeny 100-150
search_book("10142", 100, 150, prompt_1354, "nalezy_svatby_umrti_1354.csv")

print("Done searching deaths and marriages.")
