import os, sys
import google.genai

if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                k, v = line.split('=', 1)
                os.environ[k] = v

genai_client = google.genai.Client()

models = ['gemini-2.5-flash', 'gemini-3.5-flash', 'gemini-3.5-pro']
for m in models:
    try:
        res = genai_client.models.generate_content(
            model=m,
            contents=["Ahoj"]
        )
        print(f"Model {m} SUCCESS: {res.text.strip()}")
    except Exception as e:
        print(f"Model {m} FAILED: {e}")
