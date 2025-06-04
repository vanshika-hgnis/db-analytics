import streamlit as st
import pandas as pd
import pyodbc
import os
import requests
import hashlib

from dotenv import load_dotenv
from vanna.chromadb import ChromaDB_VectorStore
from vanna.ollama import Ollama




# Load environment variables
load_dotenv()

# MSSQL Connection Builder
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

# Vanna Class
class MyVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        chroma_config = {
            "persist_directory": "./vanna_chroma_storage",
            "anonymized_telemetry": False
        }
        ChromaDB_VectorStore.__init__(self, config=chroma_config)
        Ollama.__init__(self, config=config)

# Ollama health check
def ollama_health_check():
    try:
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

# Schema extraction functions
def extract_columns(vn):
    query = """
    SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
    FROM INFORMATION_SCHEMA.COLUMNS
    """
    return vn.run_sql(query)

def extract_foreign_keys(vn):
    query = """
    SELECT 
        fk.name AS FK_Name,
        tp.name AS ParentTable,
        cp.name AS ParentColumn,
        tr.name AS ReferencedTable,
        cr.name AS ReferencedColumn
    FROM 
        sys.foreign_keys fk
    INNER JOIN 
        sys.foreign_key_columns fkc ON fkc.constraint_object_id = fk.object_id
    INNER JOIN 
        sys.tables tp ON fkc.parent_object_id = tp.object_id
    INNER JOIN 
        sys.columns cp ON fkc.parent_object_id = cp.object_id AND fkc.parent_column_id = cp.column_id
    INNER JOIN 
        sys.tables tr ON fkc.referenced_object_id = tr.object_id
    INNER JOIN 
        sys.columns cr ON fkc.referenced_object_id = cr.object_id AND fkc.referenced_column_id = cr.column_id
    """
    return vn.run_sql(query)

# DDL generation
def sql_type(row):
    dtype = row['DATA_TYPE']
    length = row['CHARACTER_MAXIMUM_LENGTH']
    nullable = row['IS_NULLABLE']

    if length and dtype in ['nvarchar', 'varchar', 'char', 'nchar']:
        dtype_full = f"{dtype}({length if length != -1 else 'MAX'})"
    else:
        dtype_full = dtype

    nullable_str = "" if nullable == "NO" else " NULL"
    return f"{row['COLUMN_NAME']} {dtype_full}{nullable_str}"

def generate_ddl(columns_df, fk_df):
    ddl_list = []

    for table in columns_df['TABLE_NAME'].unique():
        tbl_cols = columns_df[columns_df['TABLE_NAME'] == table]

        ddl = f"CREATE TABLE {table} (\n"
        col_defs = []
        for _, row in tbl_cols.iterrows():
            col_defs.append(sql_type(row))

        ddl += ",\n".join(col_defs)

        fks = fk_df[fk_df['ParentTable'] == table]
        for _, fk_row in fks.iterrows():
            ddl += f",\nFOREIGN KEY ({fk_row['ParentColumn']}) REFERENCES {fk_row['ReferencedTable']}({fk_row['ReferencedColumn']})"

        ddl += "\n);"
        ddl_list.append(ddl)

    return "\n\n".join(ddl_list)

# ---------------- Streamlit APP ----------------

st.set_page_config(page_title="Vanna Mini App", layout="wide")
st.title("🧠 Vanna - Instant Database Chat")

if not ollama_health_check():
    st.error("❌ Ollama not reachable. Please check if Ollama is running.")
    st.stop()

vanna_model = MyVanna(config={
    'model': os.getenv("LLM"),
    'base_url': os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    'auto_pull': False
})

# Step 1: Connect to DB
with st.form("db_connect"):
    db_name = st.text_input("Enter Database Name:")
    connect = st.form_submit_button("Connect & Train")

if connect:
    try:
        conn_str = build_connection_string(db_name)
        vanna_model.connect_to_mssql(odbc_conn_str=conn_str)
        # vanna_model.run_sql 

        st.success("✅ Connected!")

        # Extract schema & train
        columns_df = extract_columns(vanna_model)
        fk_df = extract_foreign_keys(vanna_model)

        ddl_text = generate_ddl(columns_df, fk_df)
        vanna_model.train(ddl=ddl_text)

        st.success("✅ Training completed!")

        st.session_state['ready'] = True

    except Exception as e:
        st.error(f"❌ Connection failed: {e}")

# Step 2: Chat interface
if st.session_state.get('ready'):
    st.header("💬 Ask your database anything:")

    user_question = st.text_input("Ask:")

    if st.button("Generate SQL + Execute"):
        try:
            sql_generated = vanna_model.ask(user_question)
            st.code(sql_generated, language='sql')

            df_result = vanna_model.run_sql(sql_generated)
            st.dataframe(df_result)
        except Exception as e:
            st.error(f"Error: {e}")
