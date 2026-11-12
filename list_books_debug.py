import sys, os, json
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from mza_search.client import MZAClient
client = MZAClient()
try:
    results = client.fetch_all_results("Ivanovice")
    for r in results:
        #print(json.dumps(r, indent=2, ensure_ascii=False))
        # Find ID and types
        book_id = r.get('id', r.get('signatura', 'Unknown'))
        if not book_id and 'uuid' in r: book_id = r['uuid']
        #print(r)
        
        info = r.get('title', '')
        if 'description' in r: info += ' | ' + r['description']
        
        print(f"[{book_id}] {info}")
except Exception as e:
    print(e)
