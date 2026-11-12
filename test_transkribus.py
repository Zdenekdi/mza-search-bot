import os, sys, glob
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
# load env
with open('.env') as f:
    for line in f:
        line=line.strip()
        if line and not line.startswith('#'):
            k, v = line.split('=', 1)
            os.environ[k] = v

from mza_search.ai_reader import TranskribusReader

reader = TranskribusReader()
if not reader.available:
    print("Transkribus not available.")
    sys.exit(1)

images = sorted(glob.glob("/Users/zdenekdias/.gemini/antigravity/brain/8f3194fc-d68c-48cd-91e7-f2e4c11f74bd/.user_uploaded/*.jpg"))
for img in images:
    print(f"--- Processing {os.path.basename(img)} ---")
    text = reader.extract_text(img)
    if text:
        print(text)
    else:
        print("No text extracted.")
