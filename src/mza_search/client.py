import httpx
from .parser import MZAParser

class MZAClient:
    BASE_URL = "https://www.mza.cz/actapublica/matrika/hledani"

    def __init__(self):
        # Using httpx with HTTP/2 support
        self.client = httpx.Client(
            http2=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'cs-CZ,cs;q=0.9,en;q=0.8',
                'Upgrade-Insecure-Requests': '1',
                'Connection': 'keep-alive',
            },
            follow_redirects=True
        )

    def search_by_locality(self, locality, page=1):
        params = {
            'typ': 'obec',
            'search_by_obec': locality,
            'page': page
        }
        response = self.client.get(self.BASE_URL, params=params)
        response.raise_for_status()
        return response.text

    def fetch_all_results(self, locality):
        first_page_html = self.search_by_locality(locality, page=1)
        parser = MZAParser(first_page_html)
        all_entries = parser.parse_results()
        max_pages = parser.get_max_pages()

        for page in range(2, max_pages + 1):
            page_html = self.search_by_locality(locality, page=page)
            parser = MZAParser(page_html)
            all_entries.extend(parser.parse_results())
        
        return all_entries
