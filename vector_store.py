import chromadb
from embedder import OllamaEmbeddingFunction

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.embedding_function = OllamaEmbeddingFunction(model="mxbai-embed-large")
        self.collection = self.client.get_or_create_collection(
            name="schema_index",
            embedding_function=self.embedding_function
        )

    def build_store(self, schema_texts):
        ids = [str(i) for i in range(len(schema_texts))]
        self.collection.add(documents=schema_texts, ids=ids)

    def search(self, query, top_k=5):
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents"]
        )
        return results["documents"][0]
