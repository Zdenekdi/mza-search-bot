import os
import sys

with open('.env', 'r') as f:
    for line in f:
        if line.startswith('GEMINI_API_KEY='):
            os.environ['GEMINI_API_KEY'] = line.strip().split('=', 1)[1]

import google.genai

client = google.genai.Client()
models_to_test = ['gemini-2.5-flash', 'gemini-flash-latest', 'gemini-2.0-flash', 'gemini-1.5-flash']

for model_name in models_to_test:
    try:
        print(f"Testing {model_name}...")
        response = client.models.generate_content(
            model=model_name,
            contents='Hello'
        )
        print(f"  -> Success: {response.text.strip()}")
    except Exception as e:
        print(f"  -> Failed: {str(e)}")
