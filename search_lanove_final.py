import os
import json
import time
import subprocess
from io import BytesIO
from PIL import Image
import csv
import math
import google.genai

# Force the correct API key
from dotenv import load_dotenv
load_dotenv()  # klíč ber z .env, ne z kódu
client = google.genai.Client()

def fetch_image_via_curl(url):
    print(f"Fetching DZI metadata via curl for {url}")
    try:
        xml_content = subprocess.check_output(['curl', '-s', '-A', 'Mozilla/5.0', url]).decode('utf-8')
        if "xmlns" not in xml_content:
            return None
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_content)
        size = root.find('{http://schemas.microsoft.com/deepzoom/2008}Size')
        img_width = int(size.attrib['Width'])
        img_height = int(size.attrib['Height'])
    except Exception as e:
        print(f"Failed to fetch metadata: {e}")
        return None

    max_level = int(math.ceil(math.log(max(img_width, img_height), 2)))
    level = max_level - 1
    
    scale = 2 ** (max_level - level)
    cols = int(math.ceil(img_width / scale / 256.0))
    rows = int(math.ceil(img_height / scale / 256.0))
    
    full_img = Image.new('RGB', (cols * 256, rows * 256))
    base = url.replace('.dzi', '')
    
    for c in range(cols):
        for r in range(rows):
            tile_url = f"{base}_files/{level}/{c}_{r}.jpg"
            try:
                img_data = subprocess.check_output(['curl', '-s', '-A', 'Mozilla/5.0', tile_url])
                if len(img_data) > 1000:
                    tile = Image.open(BytesIO(img_data))
                    full_img.paste(tile, (c * 256, r * 256))
            except Exception:
                pass
    return full_img

def call_gemini(img, prompt):
    for attempt in range(3):
        try:
            res = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=[prompt, img]
            )
            return res.text
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "Quota" in err_str:
                print("Quota hit. Waiting 20s...")
                time.sleep(20)
            else:
                print(f"Error: {err_str}")
                break
    return "ERROR"

with open("lanove_dzi_links.txt") as f:
    links = [line.strip() for line in f if line.strip()]

prompt = """
Jsi expert na genealogii a kurentní písmo. Toto je sken z Lánového rejstříku (Morava, 1669-1679).
Hledej záznam obsahující příjmení "Dias", "Dyas", "Dijas", "Dijn" nebo "Deig", anebo profesi "Mlynář" ("Müller", "Molitor").
Pokud najdeš sebemenší zmínku, přesně přepiš celý příslušný řádek a uveď, co znamená. Zajímají nás jména jako Tomáš (Thomas), Jan (Joannes) atd.
Pokud tam nic z toho není, odpověz pouze slovem "NENALEZENO".
"""

results = []
# Zpracováváme všech 25 stran
for i, link in enumerate(links):
    print(f"Processing page {i+1}/25...")
    img = fetch_image_via_curl(link)
    if img:
        res = call_gemini(img, prompt)
        print(f"--- Page {i+1} Result ---")
        print(res[:200])
        results.append([link, res])
        time.sleep(1)

with open("nalezy_lanove.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for row in results:
        writer.writerow(row)

print("Done processing all 25 pages.")
