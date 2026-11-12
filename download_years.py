import json
from zoomify_downloader import download_zoomify

def main():
    with open("ahmp_hashes.json", "r") as f:
        hashes = json.load(f)
    
    # We will download pages 15, 25, 35, 45 to see the years
    pages_to_check = [15, 25, 35, 45]
    for p in pages_to_check:
        url = hashes.get(str(p))
        if url:
            print(f"Stahuji stranu {p}...")
            download_zoomify(url, f"ahmp_page_{p}.jpg")

if __name__ == "__main__":
    main()
