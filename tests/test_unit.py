import pytest
from mza_search.cli import filter_by_years
from mza_search.parser import MZAParser
from mza_search.scanner import MZAScanner
from mza_search.client import MZAClient

# --- Utility 1: filter_by_years ---
def test_filter_by_years_standard_range():
    entries = [
        {'birth': '1800-1850'},
        {'birth': '1850-1900'},
        {'birth': '1900-1950'},
    ]

    # Range 1840 to 1860 overlaps with first two entries
    filtered = filter_by_years(entries, 'birth', 1840, 1860)
    assert len(filtered) == 2
    assert {'birth': '1800-1850'} in filtered
    assert {'birth': '1850-1900'} in filtered

def test_filter_by_years_edge_cases():
    entries = [
        {'birth': '-'},              # Invalid / no range
        {'birth': ''},               # Empty string
        {'birth': 'None'},           # Text without numbers
        {'birth': '1850'},           # Single year
        {'birth': '1800, 1820-1850'} # Complex string
    ]

    filtered = filter_by_years(entries, 'birth', 1845, 1855)
    assert len(filtered) == 2
    assert {'birth': '1850'} in filtered
    assert {'birth': '1800, 1820-1850'} in filtered

def test_filter_by_years_exact_match():
    entries = [{'birth': '1850-1860'}]

    # Exact boundaries should match
    assert len(filter_by_years(entries, 'birth', 1850, 1850)) == 1
    assert len(filter_by_years(entries, 'birth', 1860, 1860)) == 1

    # Outside boundaries shouldn't match
    assert len(filter_by_years(entries, 'birth', 1840, 1849)) == 0
    assert len(filter_by_years(entries, 'birth', 1861, 1870)) == 0


# --- Utility 2: MZAParser.parse_results ---
def test_parse_results_valid_table():
    html = """
    <html><body>
        <table id="table">
            <tbody>
                <tr>
                    <td onclick="location.href='https://www.mza.cz/actapublica/matrika/detail/12345'">12345</td>
                    <td>Originator</td>
                    <td>1800-1850</td>
                    <td>1810-1860</td>
                    <td>1820-1870</td>
                    <td>Village 1, Village 2</td>
                    <td>100</td>
                    <td>Extra</td>
                </tr>
            </tbody>
        </table>
    </body></html>
    """
    parser = MZAParser(html)
    results = parser.parse_results()

    assert len(results) == 1
    assert results[0]['book_number'] == '12345'
    assert results[0]['originator'] == 'Originator'
    assert results[0]['birth'] == '1800-1850'
    assert results[0]['marriage'] == '1810-1860'
    assert results[0]['death'] == '1820-1870'
    assert results[0]['villages'] == 'Village 1, Village 2'
    assert results[0]['image_count'] == '100'
    assert results[0]['url'] == 'https://www.mza.cz/actapublica/matrika/detail/12345'

def test_parse_results_empty_or_invalid():
    # Empty string
    assert MZAParser("").parse_results() == []

    # Missing table
    assert MZAParser("<html><body><div>No table here</div></body></html>").parse_results() == []

    # Row with insufficient columns
    html_short_row = """
    <html><body><table id="table"><tbody>
        <tr><td>123</td><td>Originator</td></tr>
    </tbody></table></body></html>
    """
    assert MZAParser(html_short_row).parse_results() == []


# --- Utility 3: MZAScanner.lookup_scan_ranges ---
def test_lookup_scan_ranges(httpx_mock):
    # Mock the client request
    html = """
    <html><body>
        <div id="pill_notes">
            <table>
                <tr>
                    <td>Brno</td>
                    <td>narození: 1-150</td>
                </tr>
                <tr>
                    <td>Znojmo</td>
                    <td>úmrtí: 151 - 200</td>
                </tr>
                <tr>
                    <td>Praha</td>
                    <td>jenom text bez cisel</td>
                </tr>
            </table>
        </div>
    </body></html>
    """

    httpx_mock.add_response(text=html)

    client = MZAClient()
    scanner = MZAScanner(client)
    sections = scanner.lookup_scan_ranges("dummy_book_id")

    assert len(sections) == 2

    assert sections[0]['locality'] == 'Brno'
    assert sections[0]['range'] == 'narození: 1-150'
    assert sections[0]['start'] == 1
    assert sections[0]['end'] == 150

    assert sections[1]['locality'] == 'Znojmo'
    assert sections[1]['range'] == 'úmrtí: 151 - 200'
    assert sections[1]['start'] == 151
    assert sections[1]['end'] == 200

def test_lookup_scan_ranges_empty(httpx_mock):
    # Missing pill_notes div
    httpx_mock.add_response(text="<html><body><div>Other stuff</div></body></html>")

    client = MZAClient()
    scanner = MZAScanner(client)
    assert scanner.lookup_scan_ranges("dummy_book_id") == []
