import urllib.request
import json

view_ids = "6b2f7a97-acc3-42e7-8d30-d2b3d993d300,2905f6d4-98a5-4dd1-ab97-3e443dfe6137,ecc8fda2-4b4c-481b-9344-0d2c56690861,4cba63c0-8d54-4f7f-9c24-71eef44e6545"
url = f"https://mza.cz/aron/api/aron/apu/views?ids={view_ids}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        for item in data:
            print(json.dumps(item, indent=2)[:500])
except Exception as e:
    print(e)
