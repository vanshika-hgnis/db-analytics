import streamlit as st
from core.sql_server import SQLServerConnection
from core.schema_extractor import extract_full_schema
from core.vector_store import VectorStore
from core.prompt_builder import build_prompt
from core.llm_sql_generator import LLMSQLGenerator
from core.sql_validator import SQLValidator

st.set_page_config(page_title="Vanna Clone Lightweight", layout="wide")
st.title("🧠 Vanna Clone — Lightweight Edition")

# DB Selection / Embedding
st.header("Database Setup")

db_name = st.text_input("Enter DB Name (used for Chroma storage):")
embed_button = st.button("Extract & Embed Schema")

if embed_button and db_name:
    schema_docs = extract_full_schema()
    vs = VectorStore(db_name)
    vs.build_store(schema_docs)
    st.success("✅ Schema extracted and embedded.")

# Query Phase
st.header("Text-to-SQL Generation")

db_name_query = st.text_input("Select existing embedded DB for querying:")
user_question = st.text_area("Ask your question:")

if st.button("Generate SQL"):
    vs = VectorStore(db_name_query)
    schema_context = "\n".join(vs.search(user_question))
    prompt = build_prompt(schema_context, user_question)

    llm = LLMSQLGenerator()
    sql = llm.generate(prompt)

    st.subheader("Generated SQL")
    st.code(sql, language="sql")

    validator = SQLValidator()
    if validator.validate(sql):
        st.success("✅ SQL Valid")

        db = SQLServerConnection()
        db.connect()
        df = db.execute_query(sql)
        st.dataframe(df)
        db.close()

    else:
        st.error("❌ SQL Parsing failed.")
