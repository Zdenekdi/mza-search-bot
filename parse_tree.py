import csv
import re

for filename in ['nalezy_dias_ivanovice.csv']:
    print(f"--- Analyzing {filename} ---")
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 4: continue
            book, url, scan, text = row
            text_lower = text.lower()
            lines = text.split('\n')
            relevant_lines = [l for l in lines if 'dias' in l.lower() or 'dyas' in l.lower() or 'jakub' in l.lower() or 'františek' in l.lower() or 'mariana' in l.lower() or 'mlynář' in l.lower() or 'müllermeister' in l.lower()]
            
            if "nalezeno" in text_lower or "shod" in text_lower:
                if len(relevant_lines) > 0:
                    print(f"--- Book {book} {scan} ---")
                    for l in relevant_lines:
                        if "Na základě" in l or "obrázku" in l or "potenciální" in l or "Záznam" in l: continue
                        if len(l.strip()) < 5: continue
                        print(l.strip())
