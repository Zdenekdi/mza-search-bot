import click
from mza_search.client import MZAClient
from mza_search.scanner import MZAScanner
from mza_search.ai_reader import AIReader
from mza_search.scanner import MZAScanner
import re
import os

def filter_by_years(entries, record_type, start_year, end_year):
    filtered = []
    for entry in entries:
        raw_years = entry.get(record_type, "")
        if not raw_years or raw_years == "-":
            continue
        
        years = re.findall(r'\d{4}', raw_years)
        if not years:
            continue
        
        years = [int(y) for y in years]
        entry_start = min(years)
        entry_end = max(years)
        
        if not (entry_end < start_year or entry_start > end_year):
            filtered.append(entry)
            
    return filtered

@click.group()
def cli():
    """MZA Parish Register Search & Scan Tool"""
    pass

@cli.command()
@click.option('--locality', required=True, help='Locality name (e.g., Brno)')
@click.option('--type', type=click.Choice(['birth', 'marriage', 'death']), default='birth', help='Record type')
@click.option('--year-start', type=int, help='Start year')
@click.option('--year-end', type=int, help='End year')
def search(locality, type, year_start, year_end):
    """Search for book entries by locality and years."""
    click.echo(f"Searching for {type} records in {locality}...")
    client = MZAClient()
    try:
        entries = client.fetch_all_results(locality)
        click.echo(f"Found {len(entries)} total book entries.")
        
        if year_start or year_end:
            start = year_start or 0
            end = year_end or 2100
            entries = filter_by_years(entries, type, start, end)
            click.echo(f"Filtered to {len(entries)} entries matching years {start}-{end}.")

        for entry in entries:
            click.echo("-" * 40)
            book_id = entry['url'].split('/')[-1] if entry['url'] else "N/A"
            click.echo(f"Book: {entry['book_number']} (ID: {book_id}) | {entry['originator']}")
            click.echo(f"Years: {entry[type]}")
            click.echo(f"Link: {entry['url']}")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@cli.command()
@click.argument('book_id')
def lookup(book_id):
    """List localities and scan ranges within a book."""
    click.echo(f"Looking up sections for book {book_id}...")
    client = MZAClient()
    scanner = MZAScanner(client)
    try:
        sections = scanner.lookup_scan_ranges(book_id)
        if not sections:
            click.echo("No section info found.")
            return

        click.echo(f"{'Locality':<30} | {'Range':<20} | {'Scans'}")
        click.echo("-" * 65)
        for s in sections:
            click.echo(f"{s['locality']:<30} | {s['range']:<20} | {s['start']}-{s['end']}")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@cli.command()
@click.argument('book_id')
@click.argument('scan_number', type=int)
@click.option('--output', default=None, help='Output filename')
def download(book_id, scan_number, output):
    """Download and stitch a high-res scan image."""
    output_path = output or f"mza_{book_id}_scan_{scan_number}.jpg"
    click.echo(f"Downloading scan {scan_number} from book {book_id} to {output_path}...")
    
    client = MZAClient()
    scanner = MZAScanner(client)
    try:
        path = scanner.download_scan(book_id, scan_number, output_path)
        click.echo(f"Saved to {os.path.abspath(path)}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@cli.command()
@click.argument('book_id')
@click.option('--output-dir', default=None, help='Output directory')
@click.option('--delay', type=float, default=1.0, help='Delay between scans in seconds to prevent blocking')
def download_book(book_id, output_dir, delay):
    """Download all scans for an entire book."""
    _download_book_helper(book_id, output_dir, delay)

def _download_book_helper(book_id, output_dir, delay, scan_list=None):
    import time
    out_dir = output_dir or f"mza_book_{book_id}"
    os.makedirs(out_dir, exist_ok=True)
    click.echo(f"Preparing to download book {book_id} to {out_dir}/ ...")
    
    client = MZAClient()
    scanner = MZAScanner(client)
    
    try:
        url = f"https://www.mza.cz/actapublica/matrika/detail/{book_id}"
        response = client.client.get(url)
        import re, json
        match = re.search(r'CreateSeadragon\(\s*(\[.*?\])\s*,', response.text, re.DOTALL)
        if not match:
             match = re.search(r'(\[[\s"]*https://www\.mza\.cz/iipsrv/iipsrv\.fcgi\?Deepzoom=.*?\])', response.text, re.DOTALL)
        
        if not match:
             click.echo("Error: Could not determine total number of scans.", err=True)
             return out_dir
             
        raw_images = match.group(1).replace("'", '"')
        raw_images = re.sub(r',\s*\]', ']', raw_images)
        images = json.loads(raw_images)
        total_scans = len(images)
        click.echo(f"Found {total_scans} valid scans.")
        
        scans_to_download = scan_list if scan_list else list(range(1, total_scans + 1))
        
        for i in scans_to_download:
            if i > total_scans:
                click.echo(f"Warning: Scan {i} is out of bounds (max {total_scans}). Skipping.")
                continue
                
            output_path = os.path.join(out_dir, f"scan_{i:04d}.jpg")
            if os.path.exists(output_path):
                 click.echo(f"Scan {i}/{total_scans}: Already exists, skipping.")
                 continue
                 
            click.echo(f"Scan {i}/{total_scans}: Downloading...")
            try:
                scanner.download_scan(book_id, i, output_path)
            except Exception as e:
                click.echo(f"  -> Error downloading scan {i}: {e}", err=True)
            
            if i != scans_to_download[-1]:  # Don't sleep after the last one
                 time.sleep(delay)
                 
    except Exception as e:
        click.echo(f"Error checking book details: {e}", err=True)
        
    return out_dir

@cli.command()
@click.argument('book_id')
@click.option('--query', required=True, help='What to search for using AI')
@click.option('--scans', default=None, help='Comma-separated list of scans to check (e.g. 15,16,17)')
def search_book(book_id, query, scans):
    """Automatically download and use AI to read a book."""
    if 'GEMINI_API_KEY' not in os.environ:
         click.echo("Error: GEMINI_API_KEY environment variable is not set.", err=True)
         click.echo("Please set it before running this command: export GEMINI_API_KEY='your_key'", err=True)
         return

    scan_list = None
    if scans:
        try:
             scan_list = [int(s.strip()) for s in scans.split(',')]
        except ValueError:
             click.echo("Error: --scans must be a comma-separated list of integers.", err=True)
             return

    # 1. Download or ensure book is downloaded
    out_dir = f"mza_book_{book_id}"
    out_dir = _download_book_helper(book_id, out_dir, delay=1.0, scan_list=scan_list)
    
    # 2. Run AI Reader
    click.echo(f"\n🧠 Starting AI Analysis on book {book_id}...")
    click.echo(f"Query: '{query}'")
    if scan_list:
        click.echo(f"Restricting search to scans: {scan_list}")
        
    try:
        reader = AIReader()
        
        # We start iterating over the generator
        for filename, result in reader.search_book_directory(out_dir, query, scan_list):
            click.echo(f"\n--- Result for {filename} ---")
            if "Error" in result:
                click.echo(click.style(result, fg="red"))
            else:
                 click.echo(result)
                 
    except Exception as e:
         click.echo(f"AI Search Error: {e}", err=True)
         
if __name__ == '__main__':
    cli()

