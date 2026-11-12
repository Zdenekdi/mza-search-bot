import urllib.request
import json

uuid = "b6aceb8c-8283-473d-8373-4d2b5306e8f9"
for direction in ["before", "after"]:
    url = f"https://mza.cz/aron/api/aron/apu/{uuid}/related/{direction}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f"--- {direction} ---")
            if data and 'items' in data:
                print(f"Items: {len(data['items'])}")
                if data['items']:
                    print(json.dumps(data['items'][0], indent=2)[:500])
            else:
                print(json.dumps(data, indent=2)[:500])
    except Exception as e:
        print(f"Error {direction}: {e}")
