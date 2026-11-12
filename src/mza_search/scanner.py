import re
import math
import io
import httpx
from bs4 import BeautifulSoup
from PIL import Image

class MZAScanner:
    VIEWER_URL = "https://www.mza.cz/actapublica/matrika/detail/"
    TILE_URL_TEMPLATE = "https://www.mza.cz/actapublica/tiles/{path}/"

    def __init__(self, client: 'MZAClient') -> None:
        self.client = client  # Reuse MZAClient session

    def lookup_scan_ranges(self, book_id: str) -> list[dict]:
        url = f"{self.VIEWER_URL}{book_id}"
        response = self.client.client.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        sections = []
        
        # Scrape locality sections from the metadata tab area
        # They are usually in <tr> within #pill_notes
        notes_div = soup.find('div', id='pill_notes')
        if not notes_div:
            return []

        rows = notes_div.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 2:
                locality = cols[0].get_text(strip=True)
                range_text = cols[1].get_text(strip=True)
                
                # Extract numbers from like "130-150" or "narození: 1-10"
                nums = re.findall(r'\d+', range_text)
                if nums:
                    sections.append({
                        'locality': locality,
                        'range': range_text,
                        'start': int(nums[0]),
                        'end': int(nums[-1])
                    })
        
        return sections

    def get_image_urls(self, book_id: str) -> list[str]:
        url = f"{self.VIEWER_URL}{book_id}"
        response = self.client.client.get(url)
        
        # The subagent found: CreateSeadragon(["url1", "url2", ...], [status array], ...)
        # We need the first array argument.
        match = re.search(r'CreateSeadragon\(\s*(\[.*?\])\s*,', response.text, re.DOTALL)
        if not match:
            # Fallback: search for any array that looks like the IIPImage URLs
            match = re.search(r'(\[[\s"]*https://www\.mza\.cz/iipsrv/iipsrv\.fcgi\?Deepzoom=.*?\])', response.text, re.DOTALL)
            
        if not match:
            raise Exception("Could not find images array in page source.")
            
        import json
        try:
            # Clean up JS-style strings
            raw_images = match.group(1).replace("'", '"')
            # Handle possible trailing commas
            raw_images = re.sub(r',\s*\]', ']', raw_images)
            images = json.loads(raw_images)
            return images
        except json.JSONDecodeError:
            raise Exception("Failed to parse images info from page.")

    def get_image_info(self, book_id: str, scan_number: int) -> str:
        images = self.get_image_urls(book_id)

        if scan_number < 1 or scan_number > len(images):
            raise Exception(f"Invalid scan number {scan_number}. Book has {len(images)} scans.")
            
        return images[scan_number - 1] # This is now a full URL to the .dzi

    def download_scan(self, book_id: str, scan_number: int, output_path: str) -> str:
        dzi_url = self.get_image_info(book_id, scan_number)
        
        # 1. Fetch DZI metadata
        res = self.client.client.get(dzi_url, timeout=30)
        res.raise_for_status()
        
        # Parse DZI XML
        tile_size = int(re.search(r'TileSize="(\d+)"', res.text).group(1))
        width = int(re.search(r'Width="(\d+)"', res.text).group(1))
        height = int(re.search(r'Height="(\d+)"', res.text).group(1))
        
        # Max zoom level
        max_level = math.ceil(math.log2(max(width, height)))
        
        # Zmenšíme zoom level o 1 pro 4x rychlejší stahování (plně dostačuje pro AI)
        target_level = max_level - 1
        # Nové rozměry pro poloviční rozlišení
        target_width = math.ceil(width / 2)
        target_height = math.ceil(height / 2)
        
        num_cols = math.ceil(target_width / tile_size)
        num_rows = math.ceil(target_height / tile_size)
        
        # Construct tile URL base
        tile_base = dzi_url.replace(".dzi", "_files")
        
        full_image = Image.new('RGB', (target_width, target_height))
        print(f"Stitching {num_cols}x{num_rows} tiles for scan {scan_number} at level {target_level}...")
        print(f"Stitching {num_cols}x{num_rows} tiles for scan {scan_number}...")
        
        for r in range(num_rows):
            for c in range(num_cols):
                tile_url = f"{tile_base}/{target_level}/{c}_{r}.jpg"
                success = False
                for attempt in range(3):
                    try:
                        tile_res = self.client.client.get(tile_url, timeout=30)
                        if tile_res.status_code == 200:
                            tile_img = Image.open(io.BytesIO(tile_res.content))
                            full_image.paste(tile_img, (c * tile_size, r * tile_size))
                            success = True
                            break
                        else:
                            print(f"Warning: Attempt {attempt + 1} failed to fetch tile {c}_{r} with status {tile_res.status_code}")
                    except Exception as e:
                        print(f"Warning: Attempt {attempt + 1} failed to fetch or decode tile {c}_{r} due to error: {e}")

                if not success:
                    print(f"Error: Failed to process tile {c}_{r} after 3 attempts.")
        
        full_image.save(output_path, "JPEG", quality=90)
        return output_path
