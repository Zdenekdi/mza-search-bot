import json
import os
import urllib.request
import xml.etree.ElementTree as ET
import math
from PIL import Image
import io
import google.generativeai as genai
import concurrent.futures
import time

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-2.5-flash')

def download_zoomify_level(base_url, output_filename, reduce_levels=1):
    # 1. Získat ImageProperties.xml
    xml_url = f"{base_url}/ImageProperties.xml"
    req = urllib.request.Request(xml_url, headers={'User-Agent': 'Mozilla/5.0'})
    xml_data = urllib.request.urlopen(req, timeout=15).read()
    
    root = ET.fromstring(xml_data)
    width = int(root.attrib['WIDTH'])
    height = int(root.attrib['HEIGHT'])
    tilesize = int(root.attrib['TILESIZE'])
    
    # Spočítat počet úrovní
    max_level = math.ceil(math.log2(max(width, height) / tilesize))
    
    level = max_level - reduce_levels
    if level < 0: level = 0
        
    scale = 2 ** (max_level - level)
    level_width = math.ceil(width / scale)
    level_height = math.ceil(height / scale)
    
    cols = math.ceil(level_width / tilesize)
    rows = math.ceil(level_height / tilesize)
    
    result_image = Image.new('RGB', (level_width, level_height))
    
    def get_tile_index(z, x, y):
        idx = 0
        for l in range(z):
            lw = math.ceil(width / (2 ** (max_level - l)))
            lh = math.ceil(height / (2 ** (max_level - l)))
            idx += math.ceil(lw / tilesize) * math.ceil(lh / tilesize)
        
        lw = math.ceil(width / (2 ** (max_level - z)))
        lh = math.ceil(height / (2 ** (max_level - z)))
        c = math.ceil(lw / tilesize)
        
        idx += y * c + x
        return idx
        
    for y in range(rows):
        for x in range(cols):
            tile_idx = get_tile_index(level, x, y)
            tile_group = tile_idx // 256
            
            tile_url = f"{base_url}/TileGroup{tile_group}/{level}-{x}-{y}.jpg"
            try:
                treq = urllib.request.Request(tile_url, headers={'User-Agent': 'Mozilla/5.0'})
                tdata = urllib.request.urlopen(treq, timeout=10).read()
                img = Image.open(io.BytesIO(tdata))
                result_image.paste(img, (x * tilesize, y * tilesize))
            except Exception as e:
                pass
                
    result_image.save(output_filename)

def process_page(page_num, url):
    img_path = f"ahmp_page_{page_num}.jpg"
    print(f"[{page_num}] Stahuji obrázek...")
    try:
        download_zoomify_level(url, img_path, reduce_levels=1)
    except Exception as e:
        return f"[{page_num}] Chyba stahování: {e}"
        
    print(f"[{page_num}] Obrázek stažen. Spouštím AI analýzu...")
    
    prompt = """
    Jsi expert na čtení starých latinských a německých matričních zápisů (kurent a polokurent ze 17. století). 
    Přečti pečlivě všechny křestní záznamy na této stránce. 
    Hledáme POUZE jakýkoliv výskyt jména "Thomas" v kombinaci s příjmením podobným "Dyas" (např. Tias, Dias, Dyass, Tyyas). 
    Nezajímá nás jeho povolání ani původ.
    Vyskytuje se toto jméno (Thomas Dyas / Dias / Tias atd.) na této stránce? 
    Odpověz 'ANO' nebo 'NE'. Pokud ANO, tak přepiš onen konkrétní záznam a vysvětli, kde jsi ho našel.
    """
    
    try:
        img = Image.open(img_path)
        response = model.generate_content([prompt, img])
        text = response.text
        
        # Smazat obrázek pro úsporu místa
        os.remove(img_path)
        
        if "ANO" in text.upper():
            res = f"[{page_num}] NALEZENO NĚCO ZAJÍMAVÉHO!\n{text}\n"
            print(res)
            return res
        else:
            print(f"[{page_num}] Nic nenalezeno.")
            return f"[{page_num}] NE"
    except Exception as e:
        return f"[{page_num}] Chyba AI: {e}"

def main():
    with open("ahmp_hashes.json", "r") as f:
        hashes = json.load(f)
        
    print(f"Načteno {len(hashes)} stránek k analýze.")
    
    results = []
    # Spustíme zpracování paralelně pro zrychlení, ale ne moc vláken najednou, 
    # abychom nepřetížili API limit nebo paměť (max 3)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_page = {executor.submit(process_page, p, url): p for p, url in hashes.items()}
        for future in concurrent.futures.as_completed(future_to_page):
            p = future_to_page[future]
            try:
                res = future.result()
                results.append(res)
                if "NALEZENO" in res:
                    with open("results_positive.txt", "a") as rf:
                        rf.write(res + "\n====================\n")
            except Exception as e:
                print(f"Strana {p} vygenerovala výjimku: {e}")
            time.sleep(4.5)

    with open("results_all.txt", "w") as f:
        f.write("\n".join(results))
    print("Hotovo! Výsledky uloženy.")

if __name__ == "__main__":
    main()
