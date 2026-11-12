import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))
from mza_search.ai_reader import AIReader

reader = AIReader(mode=AIReader.MODE_GEMINI)
img_path = "mza_book_zlobice_7987/scan_0176.jpg"
if not os.path.exists(img_path):
    print("No image")
else:
    res = reader.query_image(img_path, "test")
    print("RESULT IS:")
    print(res)
