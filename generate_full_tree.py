import csv
import re

out_md = "Rodokmen_Komplet_Dias.md"
with open(out_md, "w") as f:
    f.write("# KOMPLETNÍ RODINNÝ STROM DIAS (Zlobice + Ivanovice)\n\n")
    f.write("Tento dokument spojuje data ze dvou obřích databází: prohledávání matrik Ivanovic na Hané a Zlobic (včetně Vyškova). Obsahuje strukturovaný rodokmen i veškeré zdrojové přepisy nalezené umělou inteligencí.\n\n")
    
    f.write("## ČÁST 1: Klasický Rodokmen (Od 18. do 19. století)\n\n")
    
    f.write("### Nejstarší předci (Ivanovice na Hané - počátek 18. století)\n")
    f.write("**Joannes Dyas**\n")
    f.write("- **Profese:** Mlynář (Müller).\n")
    f.write("- **Zmíněn:** 18. prosince 1710 (Kniha 1355, sken 1), záznam o křtu.\n\n")
    f.write("**Thomas Dyas**\n")
    f.write("- **Manželka:** Anna Maria (zemřela 23. dubna 1708 ve věku 60 let).\n")
    f.write("- **Poznámka:** V záznamu se uvádí 'von Bubna, Prag', což může ukazovat na původ rodu před příchodem na Moravu, anebo jde o staré označení místní lokality. V oblasti prokazatelně žili mlynáři.\n\n")

    f.write("### 1. Generace (Spojka mezi Ivanovicemi a Zlobicemi)\n")
    f.write("**Jakub Dias (Dyas/Dihas)**\n")
    f.write("- **Narozen:** cca 1774-1781 (pravděpodobně v Ivanovicích, jako potomek Joannese nebo Thomase).\n")
    f.write("- **Zemřel:** cca 10. října 1838 (Zlobice/Ivanovice, věk uváděn 57 nebo 64 let).\n")
    f.write("- **Profese:** Pachtýř (nájemní mlynář) na panském mlýně v Ivanovicích na Hané.\n")
    f.write("- **Manželka:** Mariana (zemřela 27. května 1839 nebo 1848 ve Zlobicích, č.p. 15).\n\n")
    
    f.write("### 2. Generace (Děti Jakuba a Mariany - rozvětvení rodu)\n")
    f.write("**1. František Dias**\n")
    f.write("- **Narozen:** cca 1811.\n")
    f.write("- **Profese:** Mlynářský mistr ve Zlobicích (č.p. 15).\n")
    f.write("- **Sňatek:** 13. listopadu 1838 (Zlobice) s Antonií.\n\n")
    f.write("**2. Carl Dias**\n")
    f.write("- **Profese:** Nájemce/pachtýř (Pächter) ve Zlobicích (stejně jako Jakub).\n")
    f.write("- **Manželka:** Elisabeth.\n")
    f.write("- **Děti:** Rosalia (+1838).\n\n")
    f.write("**3. Wenzel (Václav) Dyas**\n")
    f.write("- **Profese:** 'gew. Müllers. Mühlarzt' (bývalý mlynář, sekerník - opravář mlýnů).\n")
    f.write("- **Bydliště:** Vyškov č.p. 11.\n\n")
    
    f.write("### 3. Generace (Vnoučata - konec 19. století)\n")
    f.write("- **Franz Dias (syn Františka?):** Mlynářský mistr (Dům č. 2, Dornich/Trnávka). Dcera Franziska (+1880).\n")
    f.write("- **Johann Dias:** Nádeník (Dům č. 2, žil s Franzem). Syn Johann (+1880).\n")
    f.write("- **Franz Dias (syn Wenzela):** Zemřel ve věku 11 let (1880, Vyškov).\n\n")
    f.write("---\n\n")
    
    f.write("## ČÁST 2: Nalezené přepisy a překlady ze Zlobic i Ivanovic\n\n")
    
    count = 0
    for filename in ['nalezy_dias_ivanovice.csv', 'nalezy_dias_zlobice.csv']:
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) < 4: continue
                book, url, scan, text = row
                text_lower = text.lower()
                
                # Zpřísněný filtr, aby dokument neměl 1000 stran
                if "dias" in text_lower or "dyas" in text_lower or "dijas" in text_lower:
                    if "nalezeno" in text_lower or "shoda" in text_lower or "přepis" in text_lower:
                        f.write(f"### {filename.split('_')[2].upper().replace('.CSV','')} - Kniha {book}, {scan}\n")
                        f.write(f"**Odkaz:** {url}\n\n")
                        clean_text = text.replace('**', '').replace('##', '').strip()
                        f.write(f"{clean_text}\n\n---\n\n")
                        count += 1
    
    print(f"Vygenerován markdown s {count} záznamy z obou oblastí.")
