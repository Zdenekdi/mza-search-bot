import os
import json
import base64
import subprocess
from io import BytesIO
from PIL import Image
import math
import urllib.request

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

url = "https://www.mza.cz/iipsrv/iipsrv.fcgi?Deepzoom=/srv/LUN113/LUN113/216000010/216000010-00165-00000000000-000-000000000-000000107/216000010-00165-00000000000-000-000000000-000000107-00010.jp2.dzi"
xml_content = subprocess.check_output(['curl', '-s', '-A', 'Mozilla/5.0', url]).decode('utf-8')
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
load_dotenv()  # klíč ber z .env, ne z kódu
root = ET.fromstring(xml_content)
size = root.find('{http://schemas.microsoft.com/deepzoom/2008}Size')
img_width = int(size.attrib['Width'])
img_height = int(size.attrib['Height'])

max_level = int(math.ceil(math.log(max(img_width, img_height), 2)))
level = max_level - 2 # Smaller this time (1/4 size)

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

buf = BytesIO()
full_img.save(buf, format="JPEG", quality=80)
image_bytes = buf.getvalue()
print(f"Image size: {len(image_bytes)} bytes")

encoded = base64.b64encode(image_bytes).decode('utf-8')
payload = {
    "contents": [{
        "parts": [
            {"text": "Hello"},
            {"inline_data": {"mime_type": "image/jpeg", "data": encoded}}
        ]
    }]
}

req = urllib.request.Request(GEMINI_API_URL, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req) as response:
        print("Success!")
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode('utf-8')}")
