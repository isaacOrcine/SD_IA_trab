import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv("agent2-gemini/.env")

api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

print("Modelos disponíveis:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"  - {model.name}")
