import urllib.request
import json
import re

uuid = "b6aceb8c-8283-473d-8373-4d2b5306e8f9"
file_id = "9a8d4a96-4e90-47b4-a616-1a8ec474b1b4"

print("1. Fetching view for the single file ID we have...")
view_url = f"https://mza.cz/aron/api/aron/apu/views?ids={file_id}"
req = urllib.request.Request(view_url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        v_data = json.loads(response.read().decode('utf-8'))
        print(json.dumps(v_data[0] if v_data else v_data, indent=2))
except Exception as e:
    print(f"Error: {e}")

print("\n2. Fetching entity...")
url = f"https://mza.cz/aron/api/aron/apu/{uuid}/entity"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        print(response.read().decode('utf-8')[:500])
except Exception as e:
    print(f"Error: {e}")
