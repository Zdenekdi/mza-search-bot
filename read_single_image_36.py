import os, sys, time
import google.genai
from PIL import Image

from dotenv import load_dotenv
load_dotenv()  # klíč ber z .env, ne z kódu
client = google.genai.Client()

prompt = """
Jsi expert na čtení českého kurentu a švabachu.
Zde je stránka z gruntovní knihy.
1. Jaké je číslo stránky (folia) dole uprostřed (nebo v pravém rohu)?
2. Přečti velký nadpis stránky uprostřed napravo. 
3. Přečti první 3 řádky pod nadpisem.
4. Najdi v textu, jestli se tam vyskytuje jméno "Mlynář", "Dias", "Dijn", "Václav", "Pavel", "Tomáš" nebo "Jan Srednl Najdarossteig mlynář".
Dej mi přesný a detailní přepis.
"""

img_path = "/Users/zdenekdias/.gemini/antigravity/brain/8f3194fc-d68c-48cd-91e7-f2e4c11f74bd/.user_uploaded/media_1789215477485.jpg"
image = Image.open(img_path)

for attempt in range(5):
    try:
        print(f"Pokus {attempt+1} přes gemini-3.6-flash...")
        res = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=[prompt, image]
        )
        print("AI Odpoved:\n", res.text)
        break
    except Exception as e:
        print("Chyba API:", e)
        time.sleep(10)
