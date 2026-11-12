import csv
import re

valid_years = []

with open('nalezy_dias_ivanovice.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader) # skip header
    for row in reader:
        book, url, scan, text = row
        # Ignorovat falešně pozitivní Dius
        if "Parochus Dius" in text or "Dius" in text:
            continue
            
        years = re.findall(r'\b(1[6789]\d\d)\b', text)
        for y in years:
            valid_years.append((int(y), text))

valid_years.sort(key=lambda x: x[0])

print("Nejstarší nalezené platné roky (top 5):")
for y, text in valid_years[:5]:
    print(f"--- ROK {y} ---")
    print(text)
