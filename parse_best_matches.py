import csv
import re

matches = []

with open('nalezy_dias_zlobice.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader) # skip header
    for row in reader:
        if len(row) < 4: continue
        book = row[0]
        scan = row[2]
        text = row[3]
        
        # Extract everything after "Přepis záznamu:" or "Transcription:"
        prep_match = re.search(r'(Přepis[^:]*:|Transcription:)(.*?)(?:\*\*Proč|\*\*Zdůvodnění|---|$)', text, re.IGNORECASE | re.DOTALL)
        
        if prep_match:
            prepis = prep_match.group(2).strip()
            # check if the prepis actually contains Dias/Dyas/Dihas
            if re.search(r'\b(dias|dyas|dihas|dyhas|diase|diasem|dihasem)\b', prepis, re.IGNORECASE):
                matches.append({
                    'book': book,
                    'scan': scan,
                    'prepis': prepis
                })

print(f"Found {len(matches)} strong matches with the surname in the transcription.")
for i, m in enumerate(matches[:20]):
    print(f"--- Book {m['book']}, {m['scan']} ---")
    print(m['prepis'])
