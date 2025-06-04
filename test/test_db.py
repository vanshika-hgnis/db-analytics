import os
import sys

# Add the parent directory (db-analytics) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.vector_store import VectorStore


store = VectorStore("test_db")
store.collection.add(
    documents=["Test document about SQL"],
    ids=["id1"]
)

results = store.collection.query(
    query_texts=["SQL"],
    n_results=1
)

print(results)
