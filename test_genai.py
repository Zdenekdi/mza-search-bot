import google.genai
import os
from dotenv import load_dotenv
load_dotenv()  # klíč ber z .env, ne z kódu

try:
    print(f"Key in env starts with: {os.environ.get('GEMINI_API_KEY', '')[:10]}")
    client = google.genai.Client()
    res = client.models.generate_content(
        model='gemini-2.5-flash',
        contents="Hello"
    )
    print("Success with gemini-2.5-flash:", res.text)
except Exception as e:
    print("Error 2.5-flash:", e)

try:
    client = google.genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    res = client.models.generate_content(
        model='gemini-2.5-flash',
        contents="Hello"
    )
    print("Success with AQ key:", res.text)
except Exception as e:
    print("Error AQ key:", e)
