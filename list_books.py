import sys, os, json
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from mza_search.client import MZAClient
client = MZAClient()
try:
    results = client.fetch_all_results("Ivanovice na Hané")
    for r in results:
        print(f"Book {r.get('id')}: {r.get('typ', 'Unknown')} | {r.get('rok_od')} - {r.get('rok_do')}")
except Exception as e:
    print(e)
