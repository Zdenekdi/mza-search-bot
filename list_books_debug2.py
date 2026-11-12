import sys, os, json
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from mza_search.client import MZAClient
client = MZAClient()
try:
    results = client.fetch_all_results("Ivanovice")
    if results:
        print("Keys of first result:")
        print(results[0].keys())
        print(json.dumps(results[0], indent=2, ensure_ascii=False))
except Exception as e:
    print(e)
