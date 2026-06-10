import os
import google.genai

with open('.env', 'r') as f:
    for line in f:
        if line.startswith('GEMINI_API_KEY='):
            os.environ['GEMINI_API_KEY'] = line.strip().split('=', 1)[1]

client = google.genai.Client()
for model in client.models.list():
    if "flash" in model.name:
        print(model.name)
