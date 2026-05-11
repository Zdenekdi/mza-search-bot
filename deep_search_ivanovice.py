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

# Load API key from .env manually
if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            if line.startswith('GEMINI_API_KEY='):
                os.environ['GEMINI_API_KEY'] = line.strip().split('=', 1)[1]

# All book IDs for Ivanovice na Hané
BOOK_IDS = [1353, 1354, 1355, 1356, 1359, 1362, 10504, 1367, 488, 13127, 1368, 11527, 12694, 13363, 12884, 12696, 10388]
CHECKPOINT_FILE = 'checkpoint_search.json'

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
    ai_reader = AIReader()
    
    output_file = 'nalezy_dias_ivanovice.csv'
    file_exists = os.path.isfile(output_file)
    
    checkpoint = load_checkpoint()
    
    # We want to keep the file open in append mode
    with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['Kniha ID', 'Kniha Odkaz', 'Sken/Strana', 'Nalezeny Text'])
            
        print(f"Starting deep search across {len(BOOK_IDS)} books...")
        
        query = "Hledej POUZE příjmení Dias (nebo podobné varianty jako Diaz, Dius). Je na této stránce uveden někdo s tímto příjmením? Pokud ANO, vypiš stručně všechny detaily k dané osobě (datum, jméno, událost). Pokud NE, odpověz přesně slovem: NENALEZENO."

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
            
            for i in range(last_processed + 1, total_scans + 1):
                img_path = os.path.join(out_dir, f"scan_{i:04d}.jpg")
                
                # Download if missing
                if not os.path.exists(img_path):
                    print(f"  [{book_id}] Downloading {i}/{total_scans}...")
                    try:
                        scanner.download_scan(book_id, i, img_path)
                        time.sleep(0.5)
                    except Exception as e:
                        print(f"  Error downloading {i}: {e}")
                        continue
                
                # AI Analysis with exponential backoff for quota errors
                max_retries = 5
                retry_count = 0
                while retry_count < max_retries:
                    print(f"  [{book_id}] AI Analyzing {i}/{total_scans} (Attempt {retry_count+1})...")
                    try:
                        result = ai_reader.query_image(img_path, query)
                        
                        # Handle quota error strictly
                        if "RESOURCE_EXHAUSTED" in result or "quota" in result.lower():
                            wait_time = 60 * (2 ** retry_count) # 60s, 120s, 240s...
                            print(f"  !!! Quota Exceeded. Waiting {wait_time}s...")
                            time.sleep(wait_time) 
                            retry_count += 1
                            continue
                        
                        # Handle other errors
                        if "Error" in result:
                            print(f"  !!! AI Error: {result}. Retrying in 10s...")
                            time.sleep(10)
                            retry_count += 1
                            continue

                        # Success! Check if something was found
                        if "NENALEZENO" not in result.upper() and result.strip() != "":
                            print(f"  *** FOUND SOMETHING ON SCAN {i}! ***")
                            writer.writerow([
                                book_id,
                                f"https://www.mza.cz/actapublica/matrika/detail/{book_id}",
                                f"Sken {i}",
                                result.strip()
                            ])
                            csvfile.flush()
                        
                        # Mark as processed in checkpoint
                        checkpoint[book_id_str] = i
                        save_checkpoint(checkpoint)
                        time.sleep(2) # Normal delay between success requests
                        break 
                        
                    except Exception as e:
                        print(f"  Unexpected AI Error on {i}: {e}")
                        retry_count += 1
                        time.sleep(10)
                
                if retry_count == max_retries:
                    print(f"  FAILED to process scan {i} after {max_retries} attempts. Moving on to next scan but not marking as finished.")
                    # We don't update the checkpoint for this scan if it failed all retries
                    # so it will be tried again on next run.

            print(f"Finished current batch of book {book_id}")

if __name__ == "__main__":
    main()
