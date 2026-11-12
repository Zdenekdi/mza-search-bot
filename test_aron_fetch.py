import urllib.request
import json

uuid = "b6aceb8c-8283-473d-8373-4d2b5306e8f9"
url = f"https://mza.cz/aron/api/aron/dao/{uuid}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        
        file_ids = []
        if 'components' in data:
            for item in data['components']:
                for subitem in item.get('items', []):
                    if subitem.get('fileId'):
                        file_ids.append(subitem['fileId'])
        elif 'items' in data:
            for item in data['items']:
                if item.get('fileId'):
                    file_ids.append(item['fileId'])
        
        print(f"Found {len(file_ids)} file IDs.")
        if file_ids:
            print(f"First ID: {file_ids[0]}")
            
            # Now fetch the view for the first ID to get the IIIF/DZI path
            view_url = f"https://mza.cz/aron/api/aron/apu/views?ids={file_ids[0]}"
            v_req = urllib.request.Request(view_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(v_req) as v_response:
                v_data = json.loads(v_response.read().decode('utf-8'))
                print("View data:")
                print(json.dumps(v_data[0] if v_data else v_data, indent=2))
except Exception as e:
    print(e)
