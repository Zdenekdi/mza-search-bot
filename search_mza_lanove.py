import httpx
from bs4 import BeautifulSoup
import urllib.parse
import json

url = "https://www.mza.cz/actapublica/matrika/hledej"
# We can try to do a POST request to actapublica or we can just try to find the id.
# actapublica is now on mza.cz/actapublica/matrika and Lánové rejstříky are sometimes on https://www.mza.cz/actapublica/lanovy/
url_lanove = "https://www.mza.cz/actapublica/lanovy/hledej"

client = httpx.Client(verify=False)

def search_lanove():
    try:
        # Fetch the search page
        r = client.get("https://www.mza.cz/actapublica/lanovy/hledej")
        if r.status_code == 200:
            print("Lánové rejstříky exist on actapublica!")
        else:
            print(f"Lánové rejstříky path not found, status: {r.status_code}")
    except Exception as e:
        print(f"Error: {e}")

search_lanove()
