from google import genai
from google.genai import types 
import os
import json
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

def generate_answer(prompt: str, file_id: str) -> str:
    with open(f"./data/{file_id}.json", 'r') as f:
        json_content = json.load(f)
    
    json_str = json.dumps(json_content, indent=2)
    
    response = gemini_client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            f"Here is the data:\n\n{json_str}\n\n{prompt}"
        ]
    )

    return response.text

if __name__ == "__main__":
    result = generate_answer(
        "Tell me about the content of the image in the article", 
        "PMC2925951"
    )
    print(result)