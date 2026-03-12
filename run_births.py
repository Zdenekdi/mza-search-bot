import os
import subprocess
import sys

os.environ['GEMINI_API_KEY'] = 'AIzaSyBT46wEtcpu_gq_-yABiJ2MlkXp_75s1NY'

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
