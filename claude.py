import os
from dotenv import load_dotenv
from  google import genai

# Load environment variables from .env
load_dotenv()

# Configure Gemini API
client =genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def ask_claude(message: str) -> str:
    """
    Sends a message to Gemini and returns the response as a plain string.
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=message
    )
    return response.text


if __name__ == "__main__":
    result = ask_claude("Say hello and tell me what you can do")
    print(result)