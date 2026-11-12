import os, sys, time, concurrent.futures
from PIL import Image
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from mza_search.client import MZAClient
from mza_search.scanner import MZAScanner
import google.genai

if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                k, v = line.split('=', 1)
                os.environ[k] = v

client = MZAClient()
scanner = MZAScanner(client)
genai_client = google.genai.Client()

def search_book(book_id, start_scan, end_scan, prompt, output_csv):
    csv_file = open(output_csv, "a", encoding="utf-8")
    for scan_idx in range(start_scan, end_scan + 1):
        print(f"Downloading scan {scan_idx}/{end_scan} of book {book_id}...")
        try:
            img_path = scanner.download_scan(book_id, scan_idx, f"book_{book_id}_scan_{scan_idx}.jpg")
        except Exception as e:
            print(f"Error downloading scan {scan_idx}: {e}")
            continue
            
        for attempt in range(5):
            try:
                print(f"Sending scan {scan_idx} to AI...")
                img = Image.open(img_path)
                max_size = 4096
                if max(img.size) > max_size:
                    ratio = max_size / max(img.size)
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    
                def do_call():
                    return genai_client.models.generate_content(
                        model='gemini-3.5-flash-lite',
                        contents=[prompt, img]
                    )
                    
                pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
                future = pool.submit(do_call)
                response = future.result(timeout=120)
                pool.shutdown(wait=False)
                
                ans = response.text.strip()
                
                if "NENALEZENO" not in ans.upper() or len(ans) > 50:
                    print(f"!!! FOUND SOMETHING ON SCAN {scan_idx} !!!")
                    csv_file.write(f'{book_id},{scan_idx},"{ans.replace(chr(34), chr(34)+chr(34))}"\n')
                    csv_file.flush()
                else:
                    print(f"Scan {scan_idx}: NENALEZENO")
                break
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower() or "503" in str(e):
                    print(f"Quota limit hit ({e}), sleeping...")
                    time.sleep(60)
                else:
                    print(f"Error AI: {e}")
                    time.sleep(5)

prompt_marriage = """
Jsi expert na genealogii. Na tomto obrázku je matrika (pravděpodobně oddaných). 
Hledáme SVATEBNÍ ZÁZNAM (Copulati/oddáni) pro Václava (Wenzel/Wenceslaus) Dyas/Dias a Barboru (Barbara) rozenou Dvořákovou (Dvorzak). Svatba by měla proběhnout někdy mezi lety 1710 a 1717.

ÚKOL:
Pečlivě projdi záznamy. Pokud najdeš svatbu ženicha jménem Václav (Wenzel/Wenceslaus) s příjmením Dias (Dyas/Dijas) a nevěsty Barbory (Dvořákové/Dworžak), přepiš tento záznam (datum svatby, jména snoubenců a jejich otců, svědci).
Pokud se na stránce taková svatba nenachází, odpověz POUZE a jedině slovem 'NENALEZENO'.
"""

prompt_birth = """
Jsi expert na genealogii. Na tomto obrázku je matrika narozených (křtů). 
Hledáme KŘESTNÍ ZÁZNAM pro Václava (Wenzel/Wenceslaus) Dyas/Dias, narozeného cca kolem roku 1690-1695.

ÚKOL:
Pečlivě projdi záznamy. Pokud najdeš křest dítěte se jménem Václav (Wenzel/Wenceslaus) s příjmením Dias (Dyas/Dijas), přepiš tento záznam (datum křtu, jméno dítěte, jména otce a matky, kmotři). Otec by mohl být například Thomas nebo Jiří (Georgius) Dias.
Pokud se na stránce nic takového nenachází, odpověz POUZE a jedině slovem 'NENALEZENO'.
"""

import sys
if len(sys.argv) > 1 and sys.argv[1] == 'marriage':
    search_book("1355", 1, 294, prompt_marriage, "nalezy_svatba_vaclav_barbora.csv")
elif len(sys.argv) > 1 and sys.argv[1] == 'birth':
    search_book("1354", 1, 236, prompt_birth, "nalezy_narozeni_vaclav_st.csv")
