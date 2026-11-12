import csv
import re
from collections import defaultdict

people = defaultdict(list)

with open('nalezy_dias_zlobice.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if len(row) < 4: continue
        book = row[0]
        scan = row[2]
        text = row[3]
        
        # Extract everything after "Přepis záznamu:" or "Transcription:"
        prep_match = re.search(r'(Přepis[^:]*:|Transcription:)(.*?)(?:\*\*Proč|\*\*Zdůvodnění|---|$)', text, re.IGNORECASE | re.DOTALL)
        if prep_match:
            prepis = prep_match.group(2).strip()
            # Try to extract the name
            # Usually format is like "*   **Jméno zemřelého:** Der Jakob Dihas"
            name_match = re.search(r'\*\*(?:Jméno[^:]*|Namen[^:]*)\*\*(?:[^:]*:)?\s*([^\n]+)', prepis, re.IGNORECASE)
            if name_match:
                name = name_match.group(1).strip()
                # filter to those containing Dias
                if re.search(r'(dias|dyas|dihas|dyhas|dies|dijas)', name, re.IGNORECASE):
                    # extract year
                    year_match = re.search(r'\b(16\d\d|17\d\d|18\d\d)\b', text)
                    year = year_match.group(1) if year_match else "Unknown"
                    
                    # normalize name slightly
                    norm_name = re.sub(r'[^a-zA-ZáéíóúýčďěňřšťžÁÉÍÓÚÝČĎĚŇŘŠŤŽ ]', '', name).strip()
                    if norm_name:
                        people[f"{norm_name} ({year})"].append((book, scan, prepis.replace('\n', ' ')))

print(f"Unique Dias/Dies names found: {len(people)}")
for name, records in sorted(people.items()):
    if len(records) >= 1: # Print all
        print(f"\n{name} (Mentions: {len(records)})")
        print(f"Example: Book {records[0][0]}, {records[0][1]}: {records[0][2][:200]}")
