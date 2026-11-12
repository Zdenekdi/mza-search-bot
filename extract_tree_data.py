import csv
import json
import os
from google import genai
from google.genai import types

# load .env manually
api_key = None
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('GEMINI_API_KEY=') or line.startswith('GOOGLE_API_KEY='):
                api_key = line.split('=', 1)[1].strip()

client = genai.Client(api_key=api_key)

texts = []
with open('nalezy_dias_zlobice.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) >= 4:
            book, url, scan, text = row
            text_lower = text.lower()
            if ("dias" in text_lower or "dyas" in text_lower or "dijas" in text_lower):
                texts.append(f"Source: Book {book}, {scan} ({url})\n{text}")

full_text = "\n\n---\n\n".join(texts)

prompt = f"""
You are an expert genealogist. Below are all the AI transcriptions of historical parish registers for the Dias family (also spelled Dyas, Dijas). 
Extract a comprehensive and deduplicated list of all actual historical events and people related to the Dias family.
Ignore speculative text or entries where the AI says "I did not find anything" or "no match". Only extract entries where a person named Dias/Dyas is actually transcribed with a date, location, or relation.

Output a JSON array of objects, where each object represents a person in the Dias family, with the following schema:
[
  {{
    "name": "Full Name",
    "birth_year": "approximate or exact",
    "death_date": "exact date if known",
    "profession": "profession",
    "location": "village/house number",
    "parents": "names of parents",
    "spouse": "name of spouse",
    "children": ["names of children"],
    "events": [
       {{"type": "death/birth/marriage", "date": "date", "description": "full translation/transcription found in the text", "source": "Book XXX, Scan YYY"}}
    ]
  }}
]

Here is the raw data:
{full_text}
"""

try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1
        ),
    )
    
    with open("extracted_dias_tree.json", "w") as f:
        f.write(response.text)
    print("Successfully extracted tree data to extracted_dias_tree.json")
except Exception as e:
    print(f"Error: {e}")
