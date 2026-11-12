import csv
import re

keywords = ["Jakub", "František", "Mariana", "Wenzel", "Johann", "Franz", "mlynář", "Müller", "Müllermeister", "Dyas", "Dias"]

with open('nalezy_dias_zlobice.csv', 'r') as f, open('filtered_findings.md', 'w') as out:
    reader = csv.reader(f)
    count = 0
    for row in reader:
        if len(row) < 4: continue
        book, url, scan, text = row
        text_lower = text.lower()
        
        # Check if it has an actual match of our key people or exact surname "Dias"/"Dyas"
        if "dias" in text_lower or "dyas" in text_lower or "dijas" in text_lower:
            # check if it contains actual dates or transcriptions (like "*", "Datum", "Přepis")
            if "přepis" in text_lower or "datum" in text_lower or "narozen" in text_lower or "zemřel" in text_lower or "otec" in text_lower:
                out.write(f"### Kniha {book}, {scan} ([Odkaz]({url}))\n")
                out.write(f"{text}\n\n---\n\n")
                count += 1

print(f"Filtered down to {count} highly relevant records.")
