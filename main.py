from functionalities.qna import generate_answer
from functionalities.abstract_search import similarity_search

# Sẽ triển khai FastAPI sau

if __name__ == "__main__":
	response = generate_answer("Explain the main findings of the article", "PMC2925951", "default")
	print(response)
	
