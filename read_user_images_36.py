import os, glob, time
import google.genai
from PIL import Image

from dotenv import load_dotenv
load_dotenv()  # klíč ber z .env, ne z kódu
client = google.genai.Client()

prompt = """
Jsi expert na čtení českého kurentu a švabachu ze 16. a 17. století.
Podívej se na tyto obrázky z Rejstříku gruntovní knihy města Ivanovice.
Hledej jména obsahující kořen "Dias", "Dijn", "Dyas" nebo "Mlynář" (případně "Müller").
Pokud tam takové jméno uvidíš, vypiš mi přesně celý řádek, kde je zapsané, a také číslo folia (stránky), na které odkazuje.
Pokud tam nic takového není, řekni mi jen "Nic jsem nenašel."
"""

images = []
for img_path in sorted(glob.glob("/Users/zdenekdias/.gemini/antigravity/brain/8f3194fc-d68c-48cd-91e7-f2e4c11f74bd/.user_uploaded/*.jpg")):
    images.append(Image.open(img_path))

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
