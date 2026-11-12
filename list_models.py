import google.genai
import os
from dotenv import load_dotenv
load_dotenv()  # klíč ber z .env, ne z kódu
try:
    client = google.genai.Client()
    # List models via REST manually to see what's available
    import requests
    r = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={os.environ['GEMINI_API_KEY']}")
    if r.status_code == 200:
        models = r.json().get("models", [])
        for m in models:
            print(m["name"])
    else:
        print(f"Error {r.status_code}: {r.text}")
except Exception as e:
    print(e)
