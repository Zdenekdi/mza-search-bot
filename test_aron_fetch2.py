import urllib.request
import json

uuid = "b6aceb8c-8283-473d-8373-4d2b5306e8f9"
url = f"https://mza.cz/aron/api/aron/apu/{uuid}/daos"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        
        file_ids = []
        if data and isinstance(data, list):
            for d in data:
                if 'items' in d:
                    for i in d['items']:
                        if i.get('fileId'):
                            file_ids.append(i['fileId'])
        
        print(f"Found {len(file_ids)} file IDs.")
        if file_ids:
            view_url = f"https://mza.cz/aron/api/aron/apu/views?ids={file_ids[0]}"
            v_req = urllib.request.Request(view_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(v_req) as v_response:
                v_data = json.loads(v_response.read().decode('utf-8'))
                print(json.dumps(v_data[0] if v_data else v_data, indent=2))
except Exception as e:
    print(f"Error fetching DAOs: {e}")
