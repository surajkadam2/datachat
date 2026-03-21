import os
from dotenv import load_dotenv
from  google import genai
from config import GEMINI_MODEL

# Load environment variables from .env
load_dotenv()

# Configure Gemini API
client =genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def ask_claude(message: str, temperature: float = 0.0) -> str:
    """
    Sends a message to Gemini and returns the response as a plain string.
    """
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=message,
        config={
            "temperature": temperature
        }
    )
    return response.text


if __name__ == "__main__":
    result = ask_claude("Say hello and tell me what you can do")
    print(result)