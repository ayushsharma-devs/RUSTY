import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(GEMINI_MODEL)
response = model.generate_content("What is the capital of Spain?")
print(response.text)
