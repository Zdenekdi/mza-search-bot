import csv
import json
import os
import re

CSV_FILE = 'nalezy_dias_ivanovice.csv'
CLEAN_CSV = 'nalezy_dias_ivanovice_clean.csv'
CHECKPOINT_FILE = 'checkpoint_search.json'

def clean_and_checkpoint():
    if not os.path.exists(CSV_FILE):
        print(f"File {CSV_FILE} not found.")
        return

    seen = set()
    cleaned_rows = []
    checkpoint = {}

    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header:
            cleaned_rows.append(header)
        
        for row in reader:
            if not row or len(row) < 4:
                continue
            
            book_id = row[0]
            scan_text = row[2] # e.g. "Sken 123"
            find_text = row[3]
            
            # Key for deduplication: (book_id, scan_number)
            # We also check if find_text looks like an error
            if "Error" in find_text or "RESOURCE_EXHAUSTED" in find_text:
                continue
            
            dedup_key = (book_id, scan_text)
            if dedup_key in seen:
                continue
            
            seen.add(dedup_key)
            cleaned_rows.append(row)
            
            # Update checkpoint
            # Scan text is typically "Sken 123"
            match = re.search(r'(\d+)', scan_text)
            if match:
                scan_num = int(match.group(1))
                if book_id not in checkpoint or scan_num > checkpoint[book_id]:
                    checkpoint[book_id] = scan_num

    # Write cleaned CSV
    with open(CLEAN_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(cleaned_rows)
    
    # Write checkpoint
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump(checkpoint, f, indent=2)
    
    print(f"Cleaned {len(cleaned_rows)} rows (including header).")
    print(f"Deduplicated from original size.")
    print(f"Generated checkpoint for {len(checkpoint)} books.")
    
    # Replace original with clean one
    os.replace(CLEAN_CSV, CSV_FILE)

if __name__ == "__main__":
    clean_and_checkpoint()
