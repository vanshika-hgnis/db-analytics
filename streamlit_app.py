import streamlit as st
from sql_server import SQLServerConnection
from schema_extractor import extract_full_schema,build_prompt_context
from vector_store import VectorStore
from llm_generator import LLMSQLGenerator
from sql_validator import SQLValidator

st.title("🧠 Vanna Clone V9.0 — Full RAG Edition")

db = SQLServerConnection()
connected = db.connect()

if not connected:
    st.error("❌ Failed to connect to SQL Server!")
    st.stop()

# Extract schema once
schema_lines = extract_full_schema()

# Build Vector Store per DB
db_name = db.connection.getinfo(6)  # Get database name
vector_store = VectorStore(db_name)
vector_store.build_store(schema_lines)

# Initialize components
llm = LLMSQLGenerator()
validator = SQLValidator()

# UI
user_question = st.text_area("Ask your question:")

if st.button("Generate & Execute"):
    retrieved_schema = vector_store.search(user_question)
    prompt_context = build_prompt_context(retrieved_schema)

    full_sql = llm.generate_sql(prompt_context, user_question)
    st.subheader("Generated SQL")
    st.code(full_sql, language='sql')

    valid = validator.validate(full_sql)
    if not valid:
        st.warning("⚠ SQL parse failed. Execution skipped.")
        st.stop()

    try:
        df = db.execute_query(full_sql)
        st.success("✅ Query executed successfully!")
        st.dataframe(df)
    except Exception as e:
        st.error(f"❌ Execution failed: {str(e)}")

if st.button("Close Connection"):
    db.close()
    st.success("SQL Server connection closed")
