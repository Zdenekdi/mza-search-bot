import os
import io
import re
import math
import time
from pathlib import Path
from PIL import Image
import httpx
import google.genai

# Extract DZI links
dzi_links = []
with open("aron_dzi_links.txt", "r") as f:
    for line in f:
        line = line.strip()
        if line:
            dzi_links.append(line)

print(f"Loaded {len(dzi_links)} DZI links.")

# Load API KEY
from dotenv import load_dotenv
load_dotenv(override=True)
client = google.genai.Client()

http_client = httpx.Client(http2=True, headers={'User-Agent': 'Mozilla/5.0'}, follow_redirects=True)

out_dir = Path("mza_book_gruntovni_107")
out_dir.mkdir(exist_ok=True)
csv_file = open("nalezy_gruntovni_dias.csv", "a", encoding="utf-8")

def download_scan(scan_idx, dzi_url):
    output_path = out_dir / f"scan_{scan_idx:04d}.jpg"
    if output_path.exists():
        return output_path
        
    res = http_client.get(dzi_url, timeout=30)
    res.raise_for_status()
    
    tile_size = int(re.search(r'TileSize="(\d+)"', res.text).group(1))
    width = int(re.search(r'Width="(\d+)"', res.text).group(1))
    height = int(re.search(r'Height="(\d+)"', res.text).group(1))
    
    max_level = math.ceil(math.log2(max(width, height)))
    target_level = max_level - 1
    target_width = math.ceil(width / 2)
    target_height = math.ceil(height / 2)
    
    num_cols = math.ceil(target_width / tile_size)
    num_rows = math.ceil(target_height / tile_size)
    
    tile_base = dzi_url.replace(".dzi", "_files")
    full_image = Image.new('RGB', (target_width, target_height))
    
    print(f"Stitching {num_cols}x{num_rows} for scan {scan_idx}...")
    for r in range(num_rows):
        for c in range(num_cols):
            tile_url = f"{tile_base}/{target_level}/{c}_{r}.jpg"
            for attempt in range(3):
                try:
                    tile_res = http_client.get(tile_url, timeout=10)
                    if tile_res.status_code == 200:
                        tile_img = Image.open(io.BytesIO(tile_res.content))
                        full_image.paste(tile_img, (c * tile_size, r * tile_size))
                        break
                except Exception:
                    pass
    full_image.save(output_path, "JPEG", quality=90)
    return output_path

prompt = """
Jsi expert na genealogii a čtení starých gruntovních knih (pozemkových knih) z 18. a 19. století, psaných kurentem a starou němčinou/češtinou.
Hledáme zmínky o rodině "Dias", "Dyas", "Dijas" nebo "Ibias", a především jakékoliv záznamy spojené s "mlýnem", "mlynářem" (Müller, Mühl).
Přečti rukopis na obrázku. Pokud tam najdeš zápis o prodeji nebo dědictví mlýna, nebo jakoukoliv zmínku o rodině Dias/Dyas/Dijas, vypiš klíčové informace (kdo komu mlýn prodal, za jakou částku, jména manželek a dětí) a doslovný přepis nejdůležitějších pasáží.
Pokud tam tato rodina NEBO mlynář vůbec nejsou, odpověz POUZE slovem 'NENALEZENO'.
"""

print("Starting scan...")
for idx, dzi_url in enumerate(dzi_links, start=1):
    print(f"Processing scan {idx}/{len(dzi_links)}")
    img_path = download_scan(idx, dzi_url)
    
    for attempt in range(5):
        try:
            img = Image.open(img_path)
            max_size = 4096
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                img = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.Resampling.LANCZOS)
                
            resp = client.models.generate_content(
                model='gemini-3.5-flash-lite',
                contents=[prompt, img]
            )
            
            ans = resp.text.strip()
            if "NENALEZENO" not in ans.upper() or len(ans) > 50:
                print(f"!!! FOUND SOMETHING ON SCAN {idx} !!!")
                csv_file.write(f'Gruntovni1727,{idx},"{ans.replace(chr(34), chr(34)+chr(34))}"\n')
                csv_file.flush()
            break
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                print("Quota limit hit, sleeping...")
                time.sleep(60)
            else:
                print(f"Error AI: {e}")
                time.sleep(5)
