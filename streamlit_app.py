import streamlit as st
from sql_server import SQLServerConnection
from schema_extractor import extract_schema_and_data
from vector_store import VectorStore
from llm_generator import LLMGenerator
from sql_rewriter import SQLRewriter

@st.cache_resource
def load_vector_store():
    schema, relationships, join_paths, values = extract_schema_and_data()
    store = VectorStore()
    store.build_store(schema)
    return store, schema, relationships, join_paths, values

st.title("🧠 Vanna-AI Clone V6.0 — Join Path Injection Edition")

vector_store, schema, relationships, join_paths, values = load_vector_store()
llm = LLMGenerator()
rewriter = SQLRewriter()
db = SQLServerConnection()
connected = db.connect()

if not connected:
    st.error("❌ Failed to connect to SQL Server!")
    st.stop()

user_question = st.text_area("Ask your question:")

if st.button("Generate & Execute"):
    with st.spinner("Generating SQL..."):
        context = "\n\n".join(vector_store.search(user_question))
        generated_sql = llm.generate_sql(context, relationships, join_paths, values, user_question)

        st.subheader("Generated SQL (Before Rewriting)")
        st.code(generated_sql, language='sql')

        rewritten_sql = rewriter.rewrite_aliases(generated_sql)
        st.subheader("SQL After Rewriting (Final Execution)")
        st.code(rewritten_sql, language='sql')

    try:
        df = db.execute_query(rewritten_sql)
        st.success("✅ Query executed successfully!")
        st.dataframe(df)
    except Exception as e:
        st.error(f"❌ Execution failed: {str(e)}")

if st.button("Close Connection"):
    db.close()
    st.success("SQL Server connection closed")
