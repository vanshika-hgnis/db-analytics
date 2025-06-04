import chromadb
import os
from core.embedder import OllamaEmbeddingFunction


class VectorStore:
    def __init__(self, db_name):
        self.db_name = db_name
        self.path = f"./chroma_db/{db_name}"
        os.makedirs(self.path, exist_ok=True)

        # Persistent Client WITHOUT tenant (safe version for local use)
        self.client = chromadb.PersistentClient(path=self.path)

        # Initialize embedding
        self.embedding_function = OllamaEmbeddingFunction(model="mxbai-embed-large")

        self.collection = self.client.get_or_create_collection(
            name="schema_index",
            embedding_function=self.embedding_function
        )

    def build_store(self, schema_docs):
        if self.collection.count() > 0:
            print("✅ Embeddings already exist for", self.db_name)
            return
        ids = [str(i) for i in range(len(schema_docs))]
        self.collection.add(documents=schema_docs, ids=ids)
        print("✅ Schema embedded for", self.db_name)

    def search(self, question, top_k=5):
        if self.collection.count() == 0:
            return ["⚠ No embeddings found. Please embed the DB first."]
        results = self.collection.query(
            query_texts=[question],
            n_results=top_k,
            include=["documents"]
        )
        documents = results.get("documents", [])
        if not documents or not documents[0]:
            return ["⚠ No relevant schema found."]
        return documents[0]
