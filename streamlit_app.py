import streamlit as st
from sql_server import SQLServerConnection
from schema_extractor import extract_schema_text
from vector_store import VectorStore
from llm_generator import LLMGenerator

@st.cache_resource
def load_vector_store():
    schema, relationships = extract_schema_text()
    store = VectorStore()
    store.build_store(schema)
    return store, schema, relationships

st.title("🧠 Data analytics app")

vector_store, schema, relationships = load_vector_store()
llm = LLMGenerator()
db = SQLServerConnection()
connected = db.connect()

if not connected:
    st.error("❌ Failed to connect to SQL Server!")
    st.stop()

user_question = st.text_area("Ask your question:")

if st.button("Generate & Execute"):
    with st.spinner("Generating SQL..."):
        # Search vector store for related schema
        context = "\n\n".join(vector_store.search(user_question))
        generated_sql = llm.generate_sql(context, relationships, user_question)

    st.subheader("Generated SQL")
    st.code(generated_sql, language='sql')

    try:
        df = db.execute_query(generated_sql)
        st.success("✅ Query executed successfully!")
        st.dataframe(df)
    except Exception as e:
        st.error(f"❌ Execution failed: {str(e)}")

if st.button("Close Connection"):
    db.close()
    st.success("SQL Server connection closed")
