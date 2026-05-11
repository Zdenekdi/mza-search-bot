import os
import subprocess
import sys

# Load API key from .env manually
if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            if line.startswith('GEMINI_API_KEY='):
                os.environ['GEMINI_API_KEY'] = line.strip().split('=', 1)[1]

scans = ",".join(str(i) for i in range(100, 102))
query = "Najdi úmrtí osoby jménem Jakub Dias (nebo Jakob Dias). Vypiš datum úmrtí, věk a rodiště nebo bydliště."


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

print("Starting scan search using subprocess...")
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)

# Yield output line by line as it prints
for line in process.stdout:
    sys.stdout.write(line)

process.wait()
print(f"Finished with exit code: {process.returncode}")
