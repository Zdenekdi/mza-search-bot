import urllib.request
import xml.etree.ElementTree as ET
import math
from PIL import Image
import os
import io

def download_zoomify(base_url, output_filename, level=None):
    # 1. Získat ImageProperties.xml
    xml_url = f"{base_url}/ImageProperties.xml"
    req = urllib.request.Request(xml_url, headers={'User-Agent': 'Mozilla/5.0'})
    xml_data = urllib.request.urlopen(req).read()
    
    root = ET.fromstring(xml_data)
    width = int(root.attrib['WIDTH'])
    height = int(root.attrib['HEIGHT'])
    tilesize = int(root.attrib['TILESIZE'])
    
    # Spočítat počet úrovní
    max_level = math.ceil(math.log2(max(width, height) / tilesize))
    
    if level is None:
        level = max_level # stáhnout v max kvalitě
        
    scale = 2 ** (max_level - level)
    level_width = math.ceil(width / scale)
    level_height = math.ceil(height / scale)
    
    cols = math.ceil(level_width / tilesize)
    rows = math.ceil(level_height / tilesize)
    
    print(f"Stahuji úroveň {level} ({level_width}x{level_height}), {cols}x{rows} dlaždic")
    
    result_image = Image.new('RGB', (level_width, level_height))
    
    # Výpočet TileGroup
    # Zoomify ukládá dlaždice do TileGroup0, TileGroup1 atd. Každá skupina má 256 dlaždic.
    # Dlaždice jsou indexovány postupně od level 0 do max_level.
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
                tdata = urllib.request.urlopen(treq).read()
                img = Image.open(io.BytesIO(tdata))
                result_image.paste(img, (x * tilesize, y * tilesize))
            except Exception as e:
                print(f"Chyba při stahování dlaždice {tile_url}: {e}")
                
    result_image.save(output_filename)
    print(f"Uloženo jako {output_filename}")

if __name__ == "__main__":
    # Otestujeme to na stránce 5, jejíž hash najdeme ručně (nebo si ho půjčíme)
    # Z ahmp_viewer.html můžeme parsovat adresy.
    # Použijme adresu ze skriptu odposlechu (což je 5. stránka podle toho, kde jsme byli)
    url = "https://images.ahmp.cz/mrimage/ahmp/zoomify/cz/archives/CZ-321100010/NAD-156/dao/images/0006/8d80bd5d1a89f2f985052bc0f3c701a5.jpg"
    download_zoomify(url, "ahmp_page5_full.jpg")
