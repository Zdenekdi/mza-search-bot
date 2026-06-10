import csv
import os
from pathlib import Path

def generate_recommendations(csv_path='nalezy_dias_ivanovice.csv', out_path='doporuceni_dalsi_kroky.md'):
    if not os.path.exists(csv_path):
        print(f"Soubor {csv_path} neexistuje. Zatím nemáme žádné nálezy.")
        return

    findings = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            findings.append(row)

    if not findings:
        print("CSV je prázdné. Žádné nálezy zatím nejsou.")
        return

    # Basic logic to formulate recommendations based on what's found
    recommendations = []
    
    recommendations.append("# 🕵️‍♂️ Automatické doporučení pro další hledání\n")
    recommendations.append("Zde jsou návrhy vygenerované na základě nejnovějších dat nalezených robotem ve skenech.\n")
    
    # Check if there's any mention of marriages or deaths for Jakub/František
    for finding in findings:
        text = finding.get('Nalezeny Text', '').lower()
        kniha = finding.get('Kniha ID', 'Neznámá kniha')
        sken = finding.get('Sken/Strana', '')
        
        # Very simple heuristic based on keywords
        if 'svatb' in text or 'oddán' in text or 'copul' in text:
            recommendations.append(f"### 💍 Nalezena potenciální svatba v knize {kniha} ({sken})")
            recommendations.append(f"- **Text:** {finding.get('Nalezeny Text')}")
            recommendations.append("- **Doporučení:** Zkontrolujte tento zápis. Pokud jde o sňatek, zkontrolujte, zda je otec ženicha (příp. nevěsty) uveden jako žijící nebo zemřelý. To vám pomůže zúžit okno pro hledání jeho úmrtí.\n")
            
        elif 'zemřel' in text or 'úmrtí' in text or 'mort' in text or 'defunct' in text:
            recommendations.append(f"### ✝️ Nalezeno potenciální úmrtí v knize {kniha} ({sken})")
            recommendations.append(f"- **Text:** {finding.get('Nalezeny Text')}")
            recommendations.append("- **Doporučení:** Pokud se jedná o Jakuba nebo Marianu, můžete uzavřít toto období a začít hledat narození jejich dětí (nebo samotného Jakuba, pokud je uveden věk úmrtí).\n")
            
        else:
            recommendations.append(f"### 📄 Obecný nález v knize {kniha} ({sken})")
            recommendations.append(f"- **Text:** {finding.get('Nalezeny Text')}")
            recommendations.append("- **Doporučení:** Podívejte se na tento záznam a ověřte ho. Může to být narození dítěte nebo svědek/kmotr u jiné události.\n")

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(recommendations))
        
    print(f"Doporučení byla uložena do: {out_path}")

if __name__ == "__main__":
    generate_recommendations()
