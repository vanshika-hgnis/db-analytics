# DB Analytics


## Code Structure

vanna_clone_v9/
│
├── sql_server.py            ✅ (same)
├── schema_extractor.py      🔧 (upgraded extractor)
├── embedder.py              🔧 (Ollama embedding function)
├── vector_store.py          🔧 (persistent per-db vector store)
├── context_builder.py       🔧 (retrieved context builder)
├── llm_sql_generator.py     🔧 (Phi-3 full SQL generator)
├── sql_validator.py         ✅ (same)
├── streamlit_app.py         🔧 (full RAG pipeline orchestrator)
├── requirements.txt         ✅ (updated)
└── .env                     ✅ (same)
