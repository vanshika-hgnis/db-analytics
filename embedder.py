# embedder.py
from chromadb import EmbeddingFunction, Documents, Embeddings
import ollama

class OllamaEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model="mxbai-embed-large"):
        self.model = model

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for text in input:
            response = ollama.embeddings(model=self.model, prompt=text)
            embeddings.append(response['embedding'])
        return embeddings
