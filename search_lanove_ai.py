import os
import json
import time
import base64
import requests
from io import BytesIO
from PIL import Image
import csv
from dotenv import load_dotenv
load_dotenv()  # klíč ber z .env, ne z kódu

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def fetch_image(url):
    print(f"Fetching tiles for {url}...")
    base = url.replace('.dzi', '')
    img_width, img_height = 0, 0
    import xml.etree.ElementTree as ET
    try:
        r = requests.get(url, headers=HEADERS)
        root = ET.fromstring(r.content)
        size = root.find('{http://schemas.microsoft.com/deepzoom/2008}Size')
        img_width = int(size.attrib['Width'])
        img_height = int(size.attrib['Height'])
    except Exception as e:
        print(f"Failed to fetch DZI metadata: {e}")
        return None

    import math
    max_level = int(math.ceil(math.log(max(img_width, img_height), 2)))
    level = max_level - 1 # zoom out slightly
    
    scale = 2 ** (max_level - level)
    cols = int(math.ceil(img_width / scale / 256.0))
    rows = int(math.ceil(img_height / scale / 256.0))
    
    full_img = Image.new('RGB', (cols * 256, rows * 256))
    for c in range(cols):
        for r in range(rows):
            tile_url = f"{base}_files/{level}/{c}_{r}.jpg"
            try:
                tr = requests.get(tile_url, headers=HEADERS)
                if tr.status_code == 200:
                    tile = Image.open(BytesIO(tr.content))
                    full_img.paste(tile, (c * 256, r * 256))
            except:
                pass
    
    buf = BytesIO()
    full_img.save(buf, format="JPEG")
    return buf.getvalue()

def call_gemini(image_bytes, prompt):
    encoded = base64.b64encode(image_bytes).decode('utf-8')
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": encoded}}
            ]
        }]
    }
    
    for attempt in range(5):
        resp = requests.post(GEMINI_API_URL, json=payload, headers={'Content-Type': 'application/json'})
        if resp.status_code == 200:
            data = resp.json()
            try:
                return data['candidates'][0]['content']['parts'][0]['text']
            except:
                return "NENALEZENO"
        elif resp.status_code == 429:
            print("Quota hit. Waiting 60s...")
            time.sleep(60)
        else:
            print(f"API Error: {resp.status_code} {resp.text}")
            break
    return "ERROR"

with open("lanove_dzi_links.txt") as f:
    links = [line.strip() for line in f if line.strip()]

prompt = """
Zde je stránka z Lánového rejstříku (1669-1679).
Hledej záznam, který obsahuje příjmení Dias / Dyas / Dijas / Dijn / Deig nebo povolání "Mlynář" (Müller, Molitor).
Zajímají nás hlavně první jména jako Tomáš (Thomas), Jan (Joannes), případně někdo starší jako otec Tomáše.
Pokud tam jsou jména držitelů půdy, přečti a vypiš je, ať víme, jestli tam Diasové figurují.
Pokud najdeš jakoukoliv spojitost, přepiš celý řádek s vysvětlením.
Pokud tam nic takového není, napiš jen "NENALEZENO".
"""

with open("nalezy_lanove.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for i, link in enumerate(links[:5]):
        print(f"Processing page {i+1}...")
        img = fetch_image(link)
        if img:
            res = call_gemini(img, prompt)
            print(res[:200])
            writer.writerow([link, res])
            
print("Done processing first 5 pages.")
