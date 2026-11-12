import csv

out = open('all_relevant.txt', 'w')
for f in ['nalezy_dias_ivanovice.csv', 'nalezy_dias_zlobice.csv']:
    with open(f, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) < 4: continue
            text = row[3]
            tl = text.lower()
            if "dias" in tl or "dyas" in tl or "dijas" in tl or "jakub" in tl or "mariana" in tl or "antoni" in tl:
                if "nalezeno" in tl or "shod" in tl or "přepis" in tl:
                    out.write(text + "\n---\n")
out.close()
