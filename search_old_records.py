import csv

results_1354 = []
results_1355 = []

try:
    with open('nalezy_vaclav_jakub.csv', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) < 4: continue
            book, _, scan, text = row[0], row[1], row[2], row[3]
            t_lower = text.lower()
            if book == '1354':
                # Look for birth of Wenzel / Václav around 1690s
                if 'wenzel' in t_lower or 'václav' in t_lower or 'vaclav' in t_lower:
                    results_1354.append(f"Scan {scan}: {text}")
            elif book == '1355':
                # Look for marriage of Wenzel and Barbara Dvorak
                if ('wenzel' in t_lower or 'václav' in t_lower or 'vaclav' in t_lower) and ('barb' in t_lower or 'dvor' in t_lower or 'dwor' in t_lower):
                    results_1355.append(f"Scan {scan}: {text}")

    print(f"--- Book 1354 (Wenzel/Václav Births) ---")
    for r in results_1354[:10]: print(r)
    print(f"--- Book 1355 (Wenzel & Barbara Marriage) ---")
    for r in results_1355[:10]: print(r)

except Exception as e:
    print(f"Error: {e}")
