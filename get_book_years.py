import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from mza_search.client import MZAClient

def get_book_years():
    client = MZAClient()
    print("Fetching metadata for Ivanovice na Hané...")
    entries = client.fetch_all_results("Ivanovice na Hané")
    
    BOOK_IDS = [1353, 1354, 1355, 1356, 1359, 1362, 10504, 1367, 488, 13127, 1368, 11527, 12694, 13363, 12884, 12696, 10388]
    
    print("Matches:")
    for entry in entries:
        if not entry.get('url'): continue
        book_id = int(entry['url'].split('/')[-1])
        if book_id in BOOK_IDS:
            print(f"Book ID: {book_id}")
            print(f"  Births: {entry.get('birth')}")
            print(f"  Marriages: {entry.get('marriage')}")
            print(f"  Deaths: {entry.get('death')}")
            print("-" * 40)

if __name__ == "__main__":
    get_book_years()
