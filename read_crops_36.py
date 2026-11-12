import os, sys, time
import google.genai
from PIL import Image

from dotenv import load_dotenv
load_dotenv()  # klíč ber z .env, ne z kódu
client = google.genai.Client()

prompt = """
Jsi expert na čtení českého kurentu a švabachu (píše se rok 1637 a 1639).
Uživatel poslal několik ostrých výřezů z folia 105. 
Tvým úkolem je sestavit z nich souvislý příběh/přepis o tom, co se s tím mlynářským gruntem dělo.
Hledej tyto osoby a zjisti, v jakém jsou vztahu k mlýnu (chalupě mlynářské):
1. "Burckhart Dias" (a všechny tvary jména Dias). Kdo to byl a komu co platil/prodal?
2. "Václav", "Tomáš", "Pavel" - komu patřil mlýn, kdo komu co splácel?
Vypiš přesně ty části textu (klidně v modernizované češtině nebo s vysvětlivkami), kde se o nich mluví, abychom pochopili, co se v rodině Diasů v letech 1637-1639 událo.
"""

# Zpracujeme všech 5 nových obrázků
img_paths = [
    "/Users/zdenekdias/.gemini/antigravity/brain/8f3194fc-d68c-48cd-91e7-f2e4c11f74bd/.user_uploaded/media_1789217100467.png",
    "/Users/zdenekdias/.gemini/antigravity/brain/8f3194fc-d68c-48cd-91e7-f2e4c11f74bd/.user_uploaded/media_1789217145884.png",
    "/Users/zdenekdias/.gemini/antigravity/brain/8f3194fc-d68c-48cd-91e7-f2e4c11f74bd/.user_uploaded/media_1789217145938.png",
    "/Users/zdenekdias/.gemini/antigravity/brain/8f3194fc-d68c-48cd-91e7-f2e4c11f74bd/.user_uploaded/media_1789217145951.png",
    "/Users/zdenekdias/.gemini/antigravity/brain/8f3194fc-d68c-48cd-91e7-f2e4c11f74bd/.user_uploaded/media_1789217145964.png"
]

images = []
for p in img_paths:
    images.append(Image.open(p))

for attempt in range(5):
    try:
        print(f"Pokus {attempt+1} přes gemini-3.6-flash...")
        res = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=[prompt] + images
        )
        print("AI Odpoved:\n", res.text)
        break
    except Exception as e:
        print("Chyba API:", e)
        time.sleep(10)
