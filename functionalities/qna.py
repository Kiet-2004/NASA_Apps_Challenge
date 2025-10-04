import google.genai as genai
from google.genai import types
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from utils.prompts import SYSTEM_PROMPT
from pydantic import BaseModel

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

class DefaultResponse(BaseModel):
    answer: str
    context: str

class ExplainResponse(BaseModel):
    explanation: str
    examples: list[str]
    context: str

class TerminologyResponse(BaseModel):
    definition: str
    examples: list[str]
    context: str

class TableFigureResponse(BaseModel):
    caption: str
    key_findings: list[str]
    significance: str
    context: str

def generate_answer(prompt: str, file_id: str, mode: str) -> dict:
    if mode not in SYSTEM_PROMPT.keys():
        mode = "default"

    json_path = DATA_DIR / f"{file_id}.json"

    try:
        with json_path.open("r", encoding="utf-8") as f:
            json_content = json.load(f)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"JSON file '{json_path.name}' not found in data directory.") from exc
    except UnicodeDecodeError as exc:
        raise UnicodeDecodeError(
            exc.encoding,
            exc.object,
            exc.start,
            exc.end,
            f"Unable to decode JSON file '{json_path.name}' with UTF-8 encoding."
        ) from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON file '{json_path.name}' contains invalid JSON.") from exc

    json_str = json.dumps(json_content, indent=2)
    final_prompt = f"{SYSTEM_PROMPT[mode]} \n\nArticle Content: {json_str}\n\nUser Query: {prompt}"

    if mode == "default":
        response_schema = {
            "response_mime_type": "application/json",
            "response_schema": DefaultResponse,
        }

    elif mode == "explain": 
        response_schema = {
            "response_mime_type": "application/json",
            "response_schema": ExplainResponse,
        }

    elif mode == "terminology":
        response_schema = {
            "response_mime_type": "application/json",
            "response_schema": TerminologyResponse,
        }
    
    elif mode == "table/figure":
        response_schema = {
            "response_mime_type": "application/json",
            "response_schema": TableFigureResponse,
        }
    
    response = gemini_client.models.generate_content(
        model="gemini-2.0-flash",
        contents=final_prompt,
        config=response_schema
    )

    return json.loads(response.text)

if __name__ == "__main__":
    result = generate_answer(
        "Tell me about the content of the image in the article", 
        "PMC2925951",
        "default"
    )
    print(result)