import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from vanna.chromadb import ChromaDB_VectorStore
from vanna.mistral import Mistral
from vanna.remote import VannaDefault

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

# Safe LLM output extraction (handles tuple error)
def safe_extract_string(response):
    if isinstance(response, tuple):
        return response[0]
    elif isinstance(response, str):
        return response
    else:
        return str(response)

# Defensive wrapper for plotly code generation
def safe_generate_plotly_code(vanna_model, question, sql, df):
    try:
        plotly_code_raw = vanna_model.generate_plotly_code(question=question, sql=sql, df=df)
        return safe_extract_string(plotly_code_raw)
    except Exception as e:
        st.warning(f"Plotly code generation failed: {e}")
        return None

# Vanna Model Class
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

# Streamlit app setup
st.set_page_config(page_title="DB Analytics", layout="wide")
st.title("🧠 DB Analytics")

# Load model into session state once
if "vanna_model" not in st.session_state:
    st.session_state.vanna_model = MyVanna()

# Sidebar DB connection form
with st.sidebar.form("db_form"):
    db_name = st.text_input("Enter Database Name:", value=st.session_state.get("db_name", ""))
    submit = st.form_submit_button("Connect & Train")

if submit:
    try:
        conn_str = build_connection_string(db_name)
        st.session_state.conn_str = conn_str
        st.session_state.db_name = db_name

        st.session_state.vanna_model.connect_to_mssql(odbc_conn_str=conn_str)

        if not os.path.exists('./vanna_chroma_storage/index'):
            st.write("Training model for first time...")
            schema_df = st.session_state.vanna_model.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")
            plan = st.session_state.vanna_model.get_training_plan_generic(schema_df)
            st.session_state.vanna_model.train(plan=plan)
            st.success("✅ Training completed.")
        else:
            st.success("✅ Previous embeddings loaded.")

        st.session_state.ready = True

    except Exception as e:
        st.error(f"❌ Connection failed: {e}")

# Main query interface
if st.session_state.get("ready", False):
    st.header("💬 Ask Your Database")

    user_q = st.text_input("Ask your question:")

    if st.button("Ask & Run") and user_q:
        try:
            # Generate SQL
            sql = st.session_state.vanna_model.generate_sql(user_q)
            st.subheader("Generated SQL:")
            st.code(sql, language='sql')

            # Execute SQL
            df = st.session_state.vanna_model.run_sql(sql)
            st.subheader("Query Results:")
            st.dataframe(df)

            # Safely generate plotly code (handles LLM failures)
            plotly_code = safe_generate_plotly_code(st.session_state.vanna_model, user_q, sql, df)
            if plotly_code:
                fig = st.session_state.vanna_model.get_plotly_figure(plotly_code=plotly_code, df=df)
                if fig:
                    st.subheader("Chart:")
                    st.plotly_chart(fig)
            else:
                st.warning("⚠ Chart not available due to plot generation error.")

        except Exception as e:
            st.error(f"❌ Error: {e}")
