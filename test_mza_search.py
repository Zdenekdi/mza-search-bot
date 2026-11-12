import httpx
from bs4 import BeautifulSoup

def search_mza(query):
    url = "https://www.mza.cz/actapublica/matrika/hledani"
    client = httpx.Client()
    # MZA acta publica usually uses some search form
    # Let's just do a basic GET to see if we can pass a query string
    response = client.get(url, params={"obec": query})
    print("Status:", response.status_code)
    # Just look for links that look like detail/ID
    soup = BeautifulSoup(response.text, 'lxml')
    links = soup.find_all('a', href=True)
    ids = []
    for link in links:
        if 'detail/' in link['href']:
            ids.append(link['href'])
    print("Found IDs:", ids)

search_mza("Zlobice")
