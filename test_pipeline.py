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

from mza_search.ai_reader import AIReader

# We will test MODE_TRANSKRIBUS which internally uses Transkribus for text extraction and AppleLocalReader (Ollama) for analysis
reader = AIReader(mode=AIReader.MODE_TRANSKRIBUS)

# MZA Book Zlobice 7987, scan 176 (the one that failed before)
img_path = "mza_book_zlobice_7987/scan_0176.jpg"

print("Querying image...")
result = reader.query_image(img_path, "Najdi rodinu Dias.")
print("RESULT:")
print(result)
