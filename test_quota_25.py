import os

with open('.env', 'r') as f:
    for line in f:
        if line.startswith('GEMINI_API_KEY='):
            os.environ['GEMINI_API_KEY'] = line.strip().split('=', 1)[1]

import google.genai

try:
    client = google.genai.Client()
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Hello'
    )
    print("Success:", response.text)
except Exception as e:
    import traceback
    traceback.print_exc()
