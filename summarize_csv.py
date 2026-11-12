import csv
import sys
import re

matches = []

with open('nalezy_dias_zlobice.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        if len(row) < 4: continue
        book = row[0]
        scan = row[2]
        text = row[3]
        
        # Try to extract the name and short event description
        name_match = re.search(r'\*\*Nalezená shoda:\*\*(.*?)\n', text, re.IGNORECASE)
        name = name_match.group(1).strip() if name_match else "Neznámý"
        
        # Try to find year/date
        year_match = re.search(r'\b(16\d\d|17\d\d|18\d\d)\b', text)
        year = year_match.group(1) if year_match else "?"
        
        # Keep just a short snippet to avoid massive logs
        snippet = text.replace('\n', ' ')[:150]
        
        matches.append(f"Kniha {book} | {scan} | Rok: {year} | Jméno: {name} | Snippet: {snippet}...")

print(f"Total findings: {len(matches)}")
for m in matches:
    print(m)
