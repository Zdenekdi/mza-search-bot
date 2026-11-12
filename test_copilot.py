import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))
from mza_search.ai_reader import CopilotReader

reader = CopilotReader()
print("Copilot available:", reader.available)
img_path = "mza_book_zlobice_7987/scan_0176.jpg"
print("Testing vision...")
res = reader.query_image(img_path, "Přečti tento historický text psaný kurentem a najdi zmínku o rodině Dias/Dyas/Dius.")
print("RESULT:")
print(res)
