import os, sys, time
import google.genai
from PIL import Image

from dotenv import load_dotenv
load_dotenv()  # klíč ber z .env, ne z kódu
client = google.genai.Client()

prompt = """
Jsi expert na čtení českého kurentu a švabachu (píše se rok 1603 a 1604).
Uživatel poslal několik ostrých výřezů z folia 104 (levá strana téže knihy, která chronologicky předchází zápisu z roku 1637).
Tvým úkolem je najít jména na této levé straně (folio 104). Zápisy začínají roky "Letha 1603", "Letha 1604" atd.
Hledej, kdo vlastnil mlýn před rokem 1637. Vyskytuje se zde příjmení "Dias", "Dijn" nebo "Mlynář"?
Vypiš prvních pár vět z těch nejstarších odstavců (1603, 1604), abychom zjistili jméno otce Purkmistra Pavla a Václava.
"""

img_paths = [
    "/Users/zdenekdias/.gemini/antigravity/brain/8f3194fc-d68c-48cd-91e7-f2e4c11f74bd/.user_uploaded/media_1789217100467.png",
    "/Users/zdenekdias/.gemini/antigravity/brain/8f3194fc-d68c-48cd-91e7-f2e4c11f74bd/.user_uploaded/media_1789217145884.png"
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
