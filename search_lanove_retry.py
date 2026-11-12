import os, time, subprocess, csv, math, json
from io import BytesIO
from PIL import Image
import google.genai

from dotenv import load_dotenv
load_dotenv()  # klíč ber z .env, ne z kódu
client = google.genai.Client()

def fetch_image_via_curl(url):
    try:
        xml = subprocess.check_output(['curl', '-s', '-A', 'Mozilla/5.0', url]).decode('utf-8')
        if "xmlns" not in xml: return None
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml)
        size = root.find('{http://schemas.microsoft.com/deepzoom/2008}Size')
        w, h = int(size.attrib['Width']), int(size.attrib['Height'])
    except: return None
    
    max_level = int(math.ceil(math.log(max(w, h), 2)))
    level = max_level - 1
    scale = 2 ** (max_level - level)
    cols = int(math.ceil(w / scale / 256.0))
    rows = int(math.ceil(h / scale / 256.0))
    full_img = Image.new('RGB', (cols * 256, rows * 256))
    base = url.replace('.dzi', '')
    
    for c in range(cols):
        for r in range(rows):
            try:
                img_data = subprocess.check_output(['curl', '-s', '-A', 'Mozilla/5.0', f"{base}_files/{level}/{c}_{r}.jpg"])
                if len(img_data) > 1000:
                    full_img.paste(Image.open(BytesIO(img_data)), (c * 256, r * 256))
            except: pass
    return full_img

def call_gemini(img, prompt):
    for attempt in range(10):
        try:
            res = client.models.generate_content(model='gemini-3.8-flash', contents=[prompt, img])
            return res.text
        except Exception as e:
            if "429" in str(e) or "Quota" in str(e) or "503" in str(e) or "UNAVAILABLE" in str(e):
                print(f"Rate limit / 503... waiting 30s. (Attempt {attempt+1})")
                time.sleep(30)
            else:
                return f"ERROR: {e}"
    return "ERROR_TIMEOUT"

with open("lanove_dzi_links.txt") as f:
    links = [line.strip() for line in f if line.strip()]

prompt = """
Jsi expert na genealogii a kurentní písmo. Toto je sken z Lánového rejstříku (Morava, 1669-1679).
Hledej záznam obsahující příjmení "Dias", "Dyas", "Dijas", "Dijn" nebo "Deig", anebo profesi "Mlynář" ("Müller", "Molitor").
Pokud najdeš sebemenší zmínku, přesně přepiš celý příslušný řádek a uveď, co znamená. Zajímají nás jména jako Tomáš (Thomas), Jan (Joannes) atd.
Pokud tam nic z toho není, odpověz pouze slovem "NENALEZENO".
"""

# Zpracujeme zbylé stránky (11 až 25)
results = []
for i in range(10, 25):
    link = links[i]
    print(f"Processing page {i+1}/25...")
    img = fetch_image_via_curl(link)
    if img:
        res = call_gemini(img, prompt)
        if res != "NENALEZENO":
            print(f"!!! NALEZENO !!!\n{res}")
        results.append([link, res])

with open("nalezy_lanove_2.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for row in results: writer.writerow(row)
print("Done.")
