import csv
import re

matches = []

with open('nalezy_dias_zlobice.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if len(row) < 4: continue
        book = row[0]
        scan = row[2]
        text = row[3]
        
        # We know it contains 'dias', 'dyas', 'dihas', 'dyhas', 'dies'
        if re.search(r'\b(dias|dyas|dihas|dyhas|dies)\b', text, re.IGNORECASE):
            # Try to grab the prepis block or the sentence mentioning it
            prep_match = re.search(r'(Přepis[^:]*:|Transcription:)(.*?)(?:\*\*Proč|\*\*Zdůvodnění|---|$)', text, re.IGNORECASE | re.DOTALL)
            if prep_match:
                prepis = prep_match.group(2).strip()
                if re.search(r'\b(dias|dyas|dihas|dyhas|dies)\b', prepis, re.IGNORECASE):
                    # collapse newlines
                    prepis_line = re.sub(r'\s+', ' ', prepis)
                    matches.append(f"[{book} - {scan}] {prepis_line}")

print(f"Found {len(matches)} exact matches.")
for m in sorted(list(set(matches))):
    print(m)
