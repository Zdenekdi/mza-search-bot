import urllib.request
import urllib.error
import time

base_url = "https://www.mza.cz/iipsrv/iipsrv.fcgi?Deepzoom=/srv/LUN113/LUN113/216000010/216000010-00165-00000000000-000-000000000-000000107/216000010-00165-00000000000-000-000000000-000000107-"

low = 1
high = 500
max_found = 0

def check_exists(num):
    val = num * 10
    url = f"{base_url}{val:05d}.jp2.dzi"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}, method='HEAD')
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200
    except Exception:
        return False

while low <= high:
    mid = (low + high) // 2
    if check_exists(mid):
        max_found = mid
        low = mid + 1
    else:
        high = mid - 1

print(f"Max image is: {max_found*10}")

with open("lanove_dzi_links.txt", "w") as f:
    for i in range(1, max_found + 1):
        f.write(f"{base_url}{i*10:05d}.jp2.dzi\n")
print(f"Saved {max_found} links to lanove_dzi_links.txt")
