import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

try:
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents='Test API spojení. Odpověz pouze: OK.'
    )
    print("Gemini 1.5 Flash Status:", response.text.strip())
except Exception as e:
    print(e)
