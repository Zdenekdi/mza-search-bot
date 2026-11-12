import csv
import re

files = [
    'nalezy_1353_nejstarsi.csv',
    'nalezy_1354_narozeni_vaclava.csv',
    'nalezy_vaclav_jakub.csv'
]

keywords = ['pochován', 'sepult', 'umřel', 'mort', 'svatba', 'copulat', 'manželstw', 'oddán']

for file in files:
    try:
        with open(file, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 3: continue
                text = row[-1].lower()
                if 'dias' in text or 'dyas' in text or 'dijs' in text or 'dijn' in text or 'deig' in text:
                    if any(k in text for k in keywords):
                        print(f"--- Nález ve {file} ---")
                        print(row[-1][:1000])
                        print()
    except Exception as e:
        print(f"Error {file}: {e}")
