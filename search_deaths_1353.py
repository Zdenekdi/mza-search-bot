import os, sys, time, csv
from PIL import Image
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from mza_search.client import MZAClient
from mza_search.scanner import MZAScanner
import google.genai

from dotenv import load_dotenv
load_dotenv()  # klíč ber z .env, ne z kódu
scanner = MZAScanner(MZAClient())
client = google.genai.Client()

def search_book(book_id, start_scan, end_scan, prompt, output_csv):
    results = []
    # go backwards since deaths/marriages are usually at the end
    for scan_idx in range(end_scan, start_scan - 1, -1):
        print(f"[{book_id}] Scan {scan_idx}...")
        try:
            img_path = scanner.download_scan(book_id, scan_idx, f"book_{book_id}_scan_{scan_idx}.jpg")
        except: continue
        
        img = Image.open(img_path)
        img.thumbnail((2000, 2000))
        for attempt in range(10):
            try:
                res = client.models.generate_content(model='gemini-3.8-flash', contents=[prompt, img])
                txt = res.text.strip()
                if txt and txt != "NENALEZENO":
                    print(f"!!! NALEZENO na str. {scan_idx} !!!\n{txt[:200]}")
                    results.append([scan_idx, txt])
                break
            except Exception as e:
                if "429" in str(e) or "503" in str(e):
                    print(f"Quota/503 wait 30s. (Att {attempt})")
                    time.sleep(30)
                else: break
                
    with open(output_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for row in results: writer.writerow(row)

prompt_1353 = """
Hledej v této matrice sňatky (Copulati) nebo úmrtí (Defuncti).
Hledaná jména: Thomas Dijn / Dyas / Dias, Marina (manželka).
Případně Joannes Dijn (Jan st. narozen 1664).
Vypiš přesný datum, jména a text. Pokud tam nejsou, napiš jen NENALEZENO.
"""
# 1353 ends at 148, so marriages and deaths are probably from 110 to 148.
search_book("10141", 110, 148, prompt_1353, "nalezy_svatby_umrti_1353_fixed.csv")
