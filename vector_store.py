# db-analytics/vectore_store.py 

import chromadb
import os
from embedder import OllamaEmbeddingFunction

class VectorStore:
    def __init__(self, db_name):
        self.db_name = db_name
        self.path = f"./chroma_db/{db_name}"
        os.makedirs(self.path, exist_ok=True)

        self.client = chromadb.PersistentClient(path=self.path)
        self.embedding_function = OllamaEmbeddingFunction(model="mxbai-embed-large")
        self.collection = self.client.get_or_create_collection(
            name="schema_index",
            embedding_function=self.embedding_function
        )

    def build_store(self, schema_lines):
        if self.collection.count() > 0:
            print("✅ Embedding already exists for", self.db_name)
            return
        ids = [str(i) for i in range(len(schema_lines))]
        self.collection.add(documents=schema_lines, ids=ids)
        print("✅ Embedded schema for", self.db_name)

    def search(self, query, top_k=5):
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents"]
        )
        return results["documents"][0]
