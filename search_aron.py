import httpx
import json

client = httpx.Client(
    verify=False,
    headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
    }
)

def search():
    url = "https://aron.mza.cz/api/v1/search/aip"
    payload = {
        "query": "Lánové rejstříky Ivanovice na Hané",
        "limit": 10,
        "offset": 0
    }
    try:
        r = client.post(url, json=payload, timeout=30)
        if r.status_code == 200:
            data = r.json()
            for doc in data.get('results', []):
                print(f"Title: {doc.get('title')}")
                print(f"UUID: {doc.get('uuid')}")
                print(f"Description: {doc.get('description')}")
                print("---")
        else:
            print(f"Status: {r.status_code}, Text: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

search()
