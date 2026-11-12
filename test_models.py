import os

with open('.env', 'r') as f:
    for line in f:
        if line.startswith('GEMINI_API_KEY='):
            os.environ['GEMINI_API_KEY'] = line.strip().split('=', 1)[1]

import google.genai

try:
    client = google.genai.Client()
    for model in client.models.list():
        if "flash" in model.name:
            print(model.name)
except Exception as e:
    import traceback
    traceback.print_exc()
