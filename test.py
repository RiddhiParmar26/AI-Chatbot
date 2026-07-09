import google.generativeai as genai

genai.configure(api_key=api_key)

models = genai.list_models()

for model in models:
    print(model.name)

from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_KEY")