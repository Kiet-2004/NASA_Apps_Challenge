import os
import json
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_postgres import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.docstore.document import Document
from sqlalchemy import create_engine
import time 
from tqdm import tqdm

load_dotenv()
conn_str = os.getenv("PGVECTOR_CONNECTION_STR")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Ensure connection string is present
if not conn_str:
    raise RuntimeError("Environment variable PGVECTOR_CONNECTION_STR is not set")

# SQLAlchemy expects the 'postgresql' dialect name. Some providers or
# platforms return a URL starting with 'postgres://'. Convert that to
# a SQLAlchemy-friendly scheme using psycopg2. This prevents the
# "Can't load plugin: sqlalchemy.dialects:postgres" error.
if conn_str.startswith("postgres://"):
    conn_str = conn_str.replace("postgres://", "postgresql+psycopg2://", 1)

engine = create_engine(conn_str)

gemini_embeddings = GoogleGenerativeAIEmbeddings(
    google_api_key=gemini_api_key, 
    model="models/gemini-embedding-001"
)

vector_store = PGVector(
    connection=engine,
    collection_name="article_abstract_embedding",
    embeddings=gemini_embeddings
)


def load_abstracts_from_json(data_dir: str = "./data") -> List[Document]:
    documents = []
    data_path = Path(data_dir)
    
    if not data_path.exists():
        raise FileNotFoundError(f"Directory {data_dir} not found")
    
    json_files = list(data_path.glob("*.json"))
    
    if not json_files:
        print(f"No JSON files found in {data_dir}")
        return documents
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            abstract = data.get("abstract", "")
            
            if not abstract:
                print(f"Warning: No abstract found in {json_file.name}")
                continue
            
            doc = Document(
                page_content=abstract,
                metadata={
                    "source": json_file.name,
                    "file_path": str(json_file),
                    **{k: v for k, v in data.items() if k != "abstract"}
                }
            )
            documents.append(doc)
            
        except json.JSONDecodeError as e:
            print(f"Error parsing {json_file.name}: {e}")
        except Exception as e:
            print(f"Error processing {json_file.name}: {e}")
    
    print(f"Loaded {len(documents)} abstracts from {len(json_files)} JSON files")
    return documents


def embed_abstracts(data_dir: str = "./data") -> None:
    documents = load_abstracts_from_json(data_dir)
    
    if not documents:
        print("No documents to embed")
        return
    
    print(f"Embedding {len(documents)} abstracts...")
    for doc in tqdm(documents):
        vector_store.add_documents([doc])
        time.sleep(0.5)
    print("Embedding complete!")

def similarity_search(
    query: str, 
    k: int = 5,
    filter_dict: Dict[str, Any] = None
) -> List[tuple]:
    results = vector_store.similarity_search_with_score(
        query, 
        k=k,
        filter=filter_dict
    )
    return results


def print_search_results(results: List[tuple]) -> None:
    print(f"\nFound {len(results)} results:\n")
    for i, (doc, score) in enumerate(results, 1):
        print(f"Result {i} (Score: {score:.4f})")
        print(f"Source: {doc.metadata.get('source', 'Unknown')}")
        print(f"Abstract: {doc.page_content[:200]}...")
        print("-" * 80)


# Example usage
if __name__ == "__main__":
    embed_abstracts("./data")
    query = "Human stem cells research in space."
    results = similarity_search(query, k=5)
    print_search_results(results)
