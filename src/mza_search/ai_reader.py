import os
import json
from pathlib import Path
from google import genai
from google.genai import types
from PIL import Image

class AIReader:
    def __init__(self):
        # The genai.Client automatically picks up GEMINI_API_KEY from environment
        if 'GEMINI_API_KEY' not in os.environ:
            raise ValueError("GEMINI_API_KEY environment variable is missing. Please set it before using the AI tools.")
        self.client = genai.Client()
        # We use flash as it's the recommended multimodal model for general tasks
        self.model_name = 'gemini-2.0-flash'

    def query_image(self, image_path, prompt):
        """Send a single image and a prompt to the Gemini API."""
        try:
            # We can pass a PIL Image directly to generate_content
            img = Image.open(image_path)
            
            # Use generate_content to query the model with the image and text prompt
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[img, prompt]
            )
            return response.text
        except Exception as e:
            return f"Error analyzing image {image_path}: {e}"

    def search_book_directory(self, directory_path, query, scan_list=None):
        """Search through all images in a directory for a specific query.
        If scan_list is provided, only search those specific scans.
        Yields (filename, result) for each processed scan.
        """
        dir_path = Path(directory_path)
        if not dir_path.is_dir():
            raise FileNotFoundError(f"Directory {directory_path} not found.")

        # Find all jpegs
        images = sorted([f for f in dir_path.iterdir() if f.is_file() and f.suffix.lower() in ('.jpg', '.jpeg')])
        
        if scan_list:
            # Filter the images based on the provided scan numbers
            # Assuming files are named like scan_0001.jpg
            filtered_images = []
            for img in images:
                try:
                    # Extract the number from 'scan_0001.jpg'
                    num_str = img.stem.split('_')[-1]
                    scan_num = int(num_str)
                    if scan_num in scan_list:
                        filtered_images.append(img)
                except ValueError:
                    # Non-standard filename, ignore in filter
                    pass
            images = filtered_images

        if not images:
            yield None, "No valid images found to analyze."
            return

        base_prompt = f"Prohledej tento historický matriční záznam a odpověz na tento dotaz: '{query}'. Najdeš-li odpovídající osobu nebo událost, vypiš z dokumentu dohledatelné detaily."

        for img_path in images:
            yield img_path.name, self.query_image(img_path, base_prompt)
