import csv
for f in ['nalezy_1353_nejstarsi.csv', 'nalezy_1354_narozeni_vaclava.csv']:
    print(f"--- {f} ---")
    try:
        with open(f, encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) < 3: continue
                text = row[-1].lower()
                if ('pochovan' in text or 'umřel' in text or 'mort' in text or 'svatba' in text or 'copulat' in text or 'manželstw' in text or 'potwrz' in text):
                    print(row[-1])
                    print("===")
    except Exception as e:
        print(e)
