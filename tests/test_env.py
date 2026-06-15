import os
from dotenv import load_dotenv

load_dotenv()

gemini_key = os.getenv("GEMINI_API_KEY")
gemini_model = os.getenv("GEMINI_MODEL")

print("GEMINI_API_KEY carregada?", bool(gemini_key))
print("GEMINI_MODEL:", gemini_model)