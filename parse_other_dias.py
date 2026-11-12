import csv
import re

dias_records = []
try:
    with open('nalezy_vaclav_jakub.csv', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) < 4: continue
            book, _, scan, text = row[0], row[1], row[2], row[3]
            t_lower = text.lower()
            if 'dias' in t_lower or 'dyas' in t_lower or 'dijas' in t_lower or 'deig' in t_lower:
                dias_records.append(f"Kniha {book}, Sken {scan}:\n{text.strip()}\n")
except Exception as e:
    print(f"Error: {e}")

for i, rec in enumerate(dias_records[:15]):
    print(rec)
