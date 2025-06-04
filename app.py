import os
import sys
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"  # Torch fix
sys.modules['torch._classes'] = None
os.environ["STREAMLIT_WATCH_USE_POLLING"] = "true"
os.environ["STREAMLIT_WATCH_IGNORE_FILES"] = ".*\\.py"



import streamlit as st
from core.sql_server import SQLServerConnection
from core.schema_extractor import extract_full_schema
from core.vector_store import VectorStore
from core.prompt_builder import build_prompt
from core.llm_sql_generator import LLMSQLGenerator
from core.sql_validator import SQLValidator

st.set_page_config(page_title="DB Analytics", layout="wide")
st.title("🧠 DB Analytics")

# DB Connection
db = SQLServerConnection()
db.connect()

# Extract schema
schema_docs = extract_full_schema()

# Initialize vector store
vector_store = VectorStore(db_name=os.getenv("DB_NAME"))
vector_store.build_store(schema_docs)

# Initialize LLM + Validator
llm = LLMSQLGenerator()
validator = SQLValidator()

user_question = st.text_input("Ask your question to database:")

if user_question:
    relevant_schema = vector_store.search(user_question)
    schema_context = "\n".join(relevant_schema)

    prompt = build_prompt(schema_context, user_question)
    sql_query = llm.generate(prompt)

    st.subheader("Generated SQL")
    st.code(sql_query, language="sql")

    if validator.validate(sql_query):
        st.success("✅ SQL Validated")

        if st.button("Run Query"):
            try:
                df = db.execute_query(sql_query)
                st.write(df)
            except Exception as e:
                st.error(f"Query failed: {str(e)}")
    else:
        st.error("Invalid SQL generated.")

db.close()
