import os
import google.genai

if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, val = line.split('=', 1)
                os.environ[key.strip()] = val.strip()

print("Key starts with:", os.environ.get('GEMINI_API_KEY', '')[:10])

try:
    client = google.genai.Client()
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Ahoj, funguješ?'
    )
    print("Response:", response.text)
except Exception as e:
    print("Error:", e)
