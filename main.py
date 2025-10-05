from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from functionalities.qna import generate_answer
from functionalities.abstract_search import similarity_search
import os
app = FastAPI()

# ---- Request schema ----
class GenerateAnswerRequest(BaseModel):
    prompt: str
    file_id: str
    mode: str = "default"

class SimilaritySearchRequest(BaseModel):
    query: str
    k: int = 5
    filter_dict: Optional[Dict[str, Any]] = None

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test")
def test_endpoint():
    return {"message": "API is working!"}

# ---- API endpoints ----
@app.post("/similarity_search")
def api_similarity_search(req: SimilaritySearchRequest):
    print(req.query)
    results = similarity_search(req.query, req.k, req.filter_dict)
    return results

@app.post("/generate_answer")
def api_generate_answer(req: GenerateAnswerRequest):
    response = generate_answer(req.prompt, req.file_id, req.mode)
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 9000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
