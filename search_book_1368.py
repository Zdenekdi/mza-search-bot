import os
import sys
import time
from PIL import Image
import concurrent.futures

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

book_id = "1368"
start_scan = 1
end_scan = 190

csv_file = open("nalezy_book_1368_part1.csv", "a", encoding="utf-8")

def log_finding(book_id, scan_number, ans):
    csv_file.write(f'{book_id},{scan_number},"{ans.replace(chr(34), chr(34)+chr(34))}"\n')
    csv_file.flush()

print(f"Starting to scan book {book_id} from scan {start_scan} to {end_scan}...")

prompt = """
Jsi genealog. Tvým úkolem je najít úmrtí nebo jakékoliv záznamy spojené s rodinou s příjmením "Dias", "Dyas", "Dijas". Speciálně hledáme úmrtí z okruhu mlynářské rodiny z Ivanovic na Hané: Václav (Wenzel), Jan (Johann), Antonín (Antonius), Kateřina (Katharina) nebo Marie (Maria).
Pokud najdeš jakékoliv jméno Dias/Dyas/Dijas v zápisu úmrtí (jako zemřelého, nebo příbuzného), přepiš celý záznam (datum, jméno, věk, příčina úmrtí, č.p. a všechny další osoby uvedené v zápisu).
Pokud příjmení Dias v žádné podobě nevidíš, odpověz POUZE slovem 'NENALEZENO'. Nevracej nic jiného než 'NENALEZENO'.
"""

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
            response = future.result(timeout=300)
            pool.shutdown(wait=False)
            
            ans = response.text.strip()
            
            if "NENALEZENO" not in ans.upper() or len(ans) > 50:
                print(f"!!! FOUND SOMETHING ON SCAN {scan_idx} !!!")
                log_finding(book_id, scan_idx, ans)
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
