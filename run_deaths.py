import os
import subprocess
import sys

os.environ['GEMINI_API_KEY'] = 'AIzaSyBT46wEtcpu_gq_-yABiJ2MlkXp_75s1NY'

scans = ",".join(str(i) for i in range(104, 106)) # searching 2 scans for other deaths
query = "Najdi úmrtí osoby jménem Jakub Dias (nebo Jakob Dias). Ne ten záznam z 23. března 1810 na straně 93, ale nějaký jiný, pokud existuje. Vypiš datum úmrtí, věk a rodiště nebo bydliště."


cmd = [
    "./venv/bin/python3",
    "src/mza_search/cli.py",
    "search-book",
    "1368",
    "--query",
    query,
    "--scans",
    scans
]

env = os.environ.copy()
env["PYTHONPATH"] = "src"

with open("search_deaths.txt", "w") as f:
    process = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, text=True, env=env)
    process.wait()
