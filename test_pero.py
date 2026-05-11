import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from mza_search.ai_reader import AIReader

def test_pero():
    # Load .env
    if os.path.exists('.env'):
        with open('.env') as f:
            for line in f:
                if '=' in line:
                    key, val = line.strip().split('=', 1)
                    os.environ[key] = val

    if 'PERO_API_KEY' not in os.environ:
        print("PERO_API_KEY is not set in .env")
        return

    reader = AIReader(mode='pero')
    
    # Try to find a sample image in the project
    scans = list(Path('.').glob('**/scan_*.jpg'))
    if not scans:
        print("No scan_*.jpg files found to test with.")
        return
        
    test_img = str(scans[0])
    print(f"Testing PERO OCR with image: {test_img}")
    
    result = reader.query_image(test_img, "Searching for Dias")
    print("\n--- Result ---")
    print(result)

if __name__ == "__main__":
    test_pero()
