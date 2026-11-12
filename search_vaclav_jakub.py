import os
import csv
import time
import re
import json
import sys

# Add src to path so we can import mza_search
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from mza_search.client import MZAClient
from mza_search.scanner import MZAScanner
from mza_search.ai_reader import AIReader

# Load environment variables from .env manually
if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, val = line.split('=', 1)
                os.environ[key.strip()] = val.strip()
# All book IDs for Ivanovice na Hané (Oddaní 1367, Zemřelí 1368, Chvalkovice 1350)
BOOK_IDS = [1367, 1368, 1350]
CHECKPOINT_FILE = 'checkpoint_vaclav_jakub.json'

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_checkpoint(checkpoint):
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump(checkpoint, f, indent=2)

def get_total_scans(client, book_id):
    url = f"https://www.mza.cz/actapublica/matrika/detail/{book_id}"
    try:
        response = client.client.get(url)
        match = re.search(r'CreateSeadragon\(\s*(\[.*?\])\s*,', response.text, re.DOTALL)
        if not match:
             match = re.search(r'(\[[\s"]*https://www\.mza\.cz/iipsrv/iipsrv\.fcgi\?Deepzoom=.*?\])', response.text, re.DOTALL)
        if not match:
             return 0
        raw_images = match.group(1).replace("'", '"')
        raw_images = re.sub(r',\s*\]', ']', raw_images)
        images = json.loads(raw_images)
        return len(images)
    except Exception as e:
        print(f"Error getting totals for {book_id}: {e}")
        return 0

def main():
    if 'GEMINI_API_KEY' not in os.environ:
        print("!!! ERROR: GEMINI_API_KEY not found in environment variables.")
        print("Please create a '.env' file based on '.env.template' or set the variable manually.")
        return

    client = MZAClient()
    scanner = MZAScanner(client)
    ai_reader = AIReader(mode=AIReader.MODE_GEMINI)
    
    output_file = 'nalezy_vaclav_jakub.csv'
    file_exists = os.path.isfile(output_file)
    
    checkpoint = load_checkpoint()
    
    # We want to keep the file open in append mode
    with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['Kniha ID', 'Kniha Odkaz', 'Sken/Strana', 'Nalezeny Text'])
            
        print(f"Starting deep search across {len(BOOK_IDS)} books...")
        
        query = """Jsi expert na staré matriky. Přečti pečlivě všechny matriční záznamy na této stránce. 
Hledáme POUZE a EXPLICITNĚ následující tři události v Ivanovicích na Hané:
1. Křest Jakuba (Jacobus) s příjmením Dias (nebo Dyas, Dijas) narozeného zhruba 1750-1760. Otec by měl být Wenceslaus / Waclaw / Václav.
2. Svatbu Václava (Wenceslaus / Waclaw) s příjmením Dias (Dyas, Dijas) v letech 1740-1755.
3. Křest Václava (Wenceslaus / Waclaw) s příjmením Dias (Dyas, Dijas) v letech 1720-1735. Otec by mohl být Waclaw nebo Joannes.
Jsou na této stránce záznamy, které přímo odpovídají alespoň jedné z těchto událostí? 
Dávej si velký pozor, abys nemátl jiná jména. 
Pokud najdeš přesnou shodu s výše uvedeným popisem, napiš 'ANO' a celý záznam detailně přepiš a přelož (data, jména, povolání mlynáře, lokalita). Pokud ne, odpověz přesně slovem: NENALEZENO."""

        for book_id in BOOK_IDS:
            book_id_str = str(book_id)
            total_scans = get_total_scans(client, book_id)
            
            if book_id_str not in checkpoint:
                checkpoint[book_id_str] = 0
            
            last_processed = checkpoint[book_id_str]
            
            # If we've already finished this book, skip it
            if last_processed >= total_scans and total_scans > 0:
                print(f"Skipping Book {book_id} (Already finished all {total_scans} scans).")
                continue
            
            print(f"\n--- Book {book_id} (Progress: {last_processed}/{total_scans}) ---")
            if total_scans == 0:
                print(f"Could not find scan count for {book_id}. Skipping.")
                continue
            
            out_dir = f"mza_book_{book_id}"
            os.makedirs(out_dir, exist_ok=True)
            
            import concurrent.futures
            import threading
            
            download_lock = threading.Lock()

            def process_scan(i):
                img_path = os.path.join(out_dir, f"scan_{i:04d}.jpg")
                
                with download_lock:
                    if os.path.exists(img_path) and os.path.getsize(img_path) == 0:
                        os.remove(img_path)
                        
                    download_success = False
                    for d_attempt in range(5):
                        if not os.path.exists(img_path):
                            print(f"  [{book_id}] Downloading {i}/{total_scans} sequentially (Attempt {d_attempt+1})...")
                            try:
                                scanner.download_scan(book_id, i, img_path)
                                time.sleep(1) # Malá pauza, ať neshodíme archiv
                                download_success = True
                                break
                            except Exception as e:
                                print(f"  Error downloading {i}: {e}")
                                if os.path.exists(img_path):
                                    os.remove(img_path)
                                time.sleep(10)
                        else:
                            download_success = True
                            break
                            
                    if not download_success:
                        return i, False, None
                
                max_retries = 20
                retry_count = 0
                while retry_count < max_retries:
                    print(f"  [{book_id}] AI Analyzing {i}/{total_scans} (Attempt {retry_count+1})...")
                    try:
                        result = ai_reader.query_image(img_path, query)
                        
                        if "503 UNAVAILABLE" in result:
                            time.sleep(30)
                            retry_count += 1
                            continue
                        elif "RESOURCE_EXHAUSTED" in result or "quota" in result.lower():
                            print(f"  [{book_id}] Quota exhausted: {result}")
                            time.sleep(60)
                            # Záměrně nezvyšujeme retry_count, abychom počkali na denní reset!
                            continue
                        elif "Error" in result:
                            print(f"  [{book_id}] Error in API result for scan {i}: {result}")
                            time.sleep(10)
                            retry_count += 1
                            continue
                        return i, True, result.strip()
                    except concurrent.futures.TimeoutError:
                        print(f"  [{book_id}] Timeout Error for {i}, retrying...")
                        time.sleep(5)
                        retry_count += 1
                    except Exception as e:
                        time.sleep(10)
                        retry_count += 1
                return i, False, None

            chunk_size = 5
            for chunk_start in range(last_processed + 1, total_scans + 1, chunk_size):
                chunk_end = min(chunk_start + chunk_size, total_scans + 1)
                
                # Uložíme výsledky, abychom je mohli zapsat popořadě (volitelné, ale bezpečnější pro CSV)
                results_buffer = []
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    futures = [executor.submit(process_scan, i) for i in range(chunk_start, chunk_end)]
                    for future in concurrent.futures.as_completed(futures):
                        i, success, result = future.result()
                        if not success:
                            print(f"  FAILED to process scan {i} completely. Zastavuji skript, abychom nepřeskakovali skeny!")
                            import sys
                            sys.exit(1)
                        if result and "NENALEZENO" not in result.upper():
                            print(f"  *** FOUND SOMETHING ON SCAN {i}! ***")
                            results_buffer.append((i, result))
                
                # Zapíšeme nálezy z tohoto chunku
                # Setřídíme podle čísla skenu pro pořádek v CSV
                results_buffer.sort(key=lambda x: x[0])
                for i, result in results_buffer:
                    writer.writerow([
                        book_id,
                        f"https://www.mza.cz/actapublica/matrika/detail/{book_id}",
                        f"Sken {i}",
                        result
                    ])
                    csvfile.flush()
                
                # Checkpoint po dokončení celé dávky 5 stran
                checkpoint[book_id_str] = chunk_end - 1
                save_checkpoint(checkpoint)
                time.sleep(1)
            
            print(f"Finished current batch of book {book_id}")

if __name__ == "__main__":
    main()
