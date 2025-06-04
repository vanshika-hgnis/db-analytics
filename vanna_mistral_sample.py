import streamlit as st
import pandas as pd
import os
import re
from dotenv import load_dotenv
from vanna.chromadb import ChromaDB_VectorStore
from vanna.mistral import Mistral
# from vanna.chromadb_mistral import ChromaDB_Mistral

# Load environment variables
load_dotenv()

# Build MSSQL Connection String
def build_connection_string(database):
    server = os.getenv('DB_SERVER')
    username = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        "Encrypt=no;"
        "TrustServerCertificate=yes;"
        "Connection Timeout=30;"
    )
    return conn_str

# Vanna Model Class (ChromaDB + Mistral)
class MyVanna(ChromaDB_VectorStore, Mistral):
    def __init__(self):
        chroma_config = {
            "persist_directory": "./vanna_chroma_storage",
            "anonymized_telemetry": False
        }
        ChromaDB_VectorStore.__init__(self, config=chroma_config)
        Mistral.__init__(self, config={
            'api_key': os.getenv("MISTRAL_API_KEY"),
            'model': os.getenv("MISTRAL_MODEL", "mistral-tiny")
        })

# FULL SQL Extraction (Vanna Recommended)
def clean_vanna_sql(response: str) -> str:
    if not response:
        return ""

    # First try to extract inside markdown code block ```sql ... ```
    match = re.search(r"```sql\s*(.*?)```", response, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()

    # Fallback to extracting first SQL block starting from SELECT/INSERT/UPDATE/DELETE/WITH
    match = re.search(r"(SELECT|INSERT|UPDATE|DELETE|WITH).*", response, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(0).strip()

    return response.strip()

# Streamlit page setup
st.set_page_config(page_title="DB", layout="wide")
st.title("🧠 DB Analytics")

# Initialize model only once inside session state
if "vanna_model" not in st.session_state:
    st.session_state.vanna_model = MyVanna()

    # Inject Vanna SQL Guidelines
    st.session_state.vanna_model.sql_guidelines = (
        "Please generate only raw SQL queries compatible with Microsoft SQL Server (T-SQL). "
        "Do not provide explanations, comments, or markdown formatting. "
        "Only output the valid SQL query that starts with SELECT, INSERT, UPDATE, DELETE, or WITH. "
        "Do not wrap the SQL inside markdown code blocks."
    )

# Sidebar DB Connection Form
with st.sidebar.form("db_form"):
    db_name = st.text_input("Enter Database Name:", value=st.session_state.get("db_name", ""))
    submit = st.form_submit_button("Connect & Train")

if submit:
    try:
        conn_str = build_connection_string(db_name)
        st.session_state.conn_str = conn_str
        st.session_state.db_name = db_name

        st.session_state.vanna_model.connect_to_mssql(odbc_conn_str=conn_str)

        # Train embeddings only if not already present
        if not os.path.exists('./vanna_chroma_storage/index'):
            st.write("Training model for first time...")
            schema_df = st.session_state.vanna_model.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")
            plan = st.session_state.vanna_model.get_training_plan_generic(schema_df)
            st.session_state.vanna_model.train(plan=plan)
            st.success("✅ Training completed and embeddings saved.")
        else:
            st.success("✅ Previous embeddings loaded — no retraining required.")

        st.session_state.ready = True

    except Exception as e:
        st.error(f"❌ Connection failed: {e}")

# Main Question Interface
if st.session_state.get('ready', False):
    st.header("💬 Ask Your Database")

    user_q = st.text_input("Ask your question:")

    if st.button("Generate SQL + Execute") and user_q:
        try:
            sql_generated = st.session_state.vanna_model.ask(user_q)
            sql = st.session_state.vanna_model.extract_sql(sql_generated)
            st.code(sql_generated, language='sql')

            pure_sql = clean_vanna_sql(sql_generated)

            # df_result = st.session_state.vanna_model.run_sql(pure_sql)
            # sql_run, df_result, fig = st.session_state.vanna_model.run_sql(pure_sql)
            df_result = st.session_state.vanna_model.run_sql(sql)

            st.subheader("✅ Executed SQL:")
            st.code(pure_sql,language='sql')

            st.subheader("Extracted SQL")
            st.code(sql,language='sql')

            st.subheader("📊 Query Results:")
            st.dataframe(df_result)
        
        except Exception as e:
            st.error(f"❌ Error: {e}")
