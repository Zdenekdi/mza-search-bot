from bs4 import BeautifulSoup
import re

class MZAParser:
    def __init__(self, html: str) -> None:
        self.soup = BeautifulSoup(html, 'lxml')

    def parse_results(self) -> list[dict]:
        table = self.soup.find('table', id='table')
        if not table:
            return []

        entries = []
        rows = table.find('tbody').find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 8:
                continue

            # Extracting record ID from onclick or title
            book_number_cell = cols[0]
            record_url = None
            if 'onclick' in book_number_cell.attrs:
                match = re.search(r"'(https://www.mza.cz/actapublica/matrika/detail/\d+)'", book_number_cell['onclick'])
                if match:
                    record_url = match.group(1)

            entry = {
                'book_number': cols[0].get_text(strip=True),
                'originator': cols[1].get_text(strip=True),
                'birth': cols[2].get_text(strip=True),
                'marriage': cols[3].get_text(strip=True),
                'death': cols[4].get_text(strip=True),
                'villages': cols[5].get_text(strip=True),
                'image_count': cols[6].get_text(strip=True),
                'url': record_url
            }
            entries.append(entry)
        return entries

    def get_max_pages(self) -> int:
        pagination = self.soup.find('ul', class_='pagination')
        if not pagination:
            return 1
        
        pages = []
        for a in pagination.find_all('a'):
            text = a.get_text(strip=True)
            if text.isdigit():
                pages.append(int(text))
        
        return max(pages) if pages else 1
