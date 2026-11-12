import os
import sys
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("No GEMINI_API_KEY found.")
    sys.exit(1)

client = genai.Client(api_key=api_key)

print("Reading 2MB file...")
with open("all_relevant.txt", "r") as f:
    data = f.read()

prompt = """
Jsi špičkový profesionální genealog. Tvým úkolem je zpracovat obrovské množství textových přepisů z matrik a zrekonstruovat naprosto detailní a vyčerpávající rodokmen rodiny Dias (varianty Dyas, Dijas) žijící v Ivanovicích na Hané, Zlobicích a Vyškově.

Níže ti předkládám kompletní surová data (přepisy), která jsme z matrik extrahovali.
Pečlivě si vše přečti a extrahuj:
1. VŠECHNY osoby (včetně žen - manželek s jejich rodnými jmény, dcer).
2. Přesná data narození, sňatků a úmrtí (a příčiny úmrtí, věk).
3. Lokality a čísla popisná (např. Zlobice 15, Zlobice 30, Trnávka 2).
4. Svědky a kmotry (zmiň je u daných rodin v poznámkách).
5. Kdo je čí rodič a kdo koho vzal.

VÝSTUP musí obsahovat:
1) DETAILNÍ RODOKMEN V MARKDOWNU. Zorganizuj ho do logických bloků (tzv. rodinných listů). Pro každou rodinu (např. "Rodina Františka Diase a Antonie") vypiš všechny výše zmíněné detaily, dcery (např. Antonia, 28 let), syny, čísla domů. Dovolena je jakákoliv délka. Nevynechej žádnou ženu ani dítě!
2) GEDCOM formát. Po markdownu napiš sekci "```gedcom" a vygeneruj validní textový obsah GEDCOM souboru obsahující všechny tyto osoby, aby to uživatel mohl importovat. 

Surová data:
""" + data

print("Sending to Gemini 2.5 Pro (this might take a few minutes)...")
response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents=prompt,
    config=types.GenerateContentConfig(
        temperature=0.0
    )
)

out_text = response.text
with open("Gemini_Vystup.txt", "w") as f:
    f.write(out_text)

# Rozdělení na MD a GEDCOM
if "```gedcom" in out_text:
    parts = out_text.split("```gedcom")
    md_part = parts[0]
    gedcom_part = parts[1].replace("```", "").strip()
else:
    md_part = out_text
    gedcom_part = ""

with open("Kompletni_Rodokmen_S_Detaily.md", "w") as f:
    f.write(md_part)

with open("rodokmen_dias_komplet_novy.ged", "w") as f:
    f.write(gedcom_part)

print("Dokončeno! Soubory byly vygenerovány.")
