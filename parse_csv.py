import csv, sys

with open('nalezy_vaclav_jakub.csv', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader) # skip header
    for row in reader:
        if len(row) >= 4 and row[0] == '1355':
            text = row[3]
            if any(name in text.lower() for name in ['wenzel', 'václav', 'anton', 'dvor']):
                print(f"--- Sken {row[2]} ---")
                print(text)
