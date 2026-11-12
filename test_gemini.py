import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))

if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, val = line.split('=', 1)
                os.environ[key.strip()] = val.strip()

from mza_search.ai_reader import GeminiReader

reader = GeminiReader()
img_path = "mza_book_zlobice_7987/scan_0225.jpg"
res = reader.query_image(img_path, "TEST")
print("RESULT:")
print(res)
