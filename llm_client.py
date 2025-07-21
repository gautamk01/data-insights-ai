# llm_client.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(
    "gemini-2.0-flash",
    generation_config=genai.types.GenerationConfig(
        response_mime_type="application/json"
    )
)


def ask_gemini(prompt: str) -> str:
    """Return Gemini response text."""
    response = model.generate_content(prompt)
    return response.text.strip()
