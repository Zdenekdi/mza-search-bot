import os
import subprocess
import sys

# Load API key from .env manually
if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            if line.startswith('GEMINI_API_KEY='):
                os.environ['GEMINI_API_KEY'] = line.strip().split('=', 1)[1]

scans = ",".join(str(i) for i in range(65, 67)) # searching 2 scans for births
query = "Najdi narození dětí s příjmením Dias (nebo podobně). Uveď datum, jméno dítěte a odkud rodina pochází (případně zmínku o mlýně)."


cmd = [
    "./venv/bin/python3",
    "src/mza_search/cli.py",
    "search-book",
    "1359",
    "--query",
    query,
    "--scans",
    scans
]

env = os.environ.copy()
env["PYTHONPATH"] = "src"

with open("search_births.txt", "w") as f:
    process = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, text=True, env=env)
    process.wait()
