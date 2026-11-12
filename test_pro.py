import os
import google.genai

from dotenv import load_dotenv
load_dotenv()  # klíč ber z .env, ne z kódu
try:
    client = google.genai.Client()
    res = client.models.generate_content(
        model='gemini-2.5-pro',
        contents="Hello"
    )
    print("Success with gemini-2.5-pro:", res.text)
except Exception as e:
    print("Error 2.5-pro:", e)
