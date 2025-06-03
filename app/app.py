import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
import requests
from db_connector import build_connection_string
from vanna_manager import MyVanna, calculate_schema_hash
from scheduler import load_training_state, save_training_state

# Load .env
load_dotenv()

# Ollama health check
def ollama_health_check():
    try:
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

# Streamlit Start
st.set_page_config(page_title="DB Analytics", layout="wide")
st.title("DB Analytics")

# Ollama check
if not ollama_health_check():
    st.error("❌ Ollama not reachable.")
    st.stop()

# Initialize Vanna safely
vanna_model = MyVanna(config={
    'model': os.getenv("LLM"),
    'base_url': os.getenv("OLLAMA_BASE_URL"),
    'auto_pull': False
})

# DB Connection form
with st.form("connect_form"):
    db_name = st.text_input("Enter Database Name:")
    submit = st.form_submit_button("Connect")

if submit:
    try:
        conn_str = build_connection_string(db_name)
        vanna_model.connect_to_mssql(odbc_conn_str=conn_str)
        # vanna_model.run_sql

        st.success("✅ Connected to MSSQL.")

        schema_df = vanna_model.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")
        current_hash = calculate_schema_hash(schema_df)

        state = load_training_state()
        prev_hash = state.get(db_name)

        if current_hash != prev_hash:
            st.write("🔄 Schema changed. Training...")
            plan = vanna_model.get_training_plan_generic(schema_df)
            vanna_model.train(plan=plan)
            save_training_state({db_name: current_hash})
            st.success("✅ Retraining completed.")
        else:
            st.success("✅ Schema unchanged. Skipping retraining.")

        st.session_state['connected'] = True

    except Exception as e:
        st.error(f"❌ Connection failed: {e}")

# Additional manual training
if st.session_state.get('connected'):
    st.header("Add Example SQL Training")

    with st.form("example_form"):
        question = st.text_area("Question")
        sql = st.text_area("SQL Query")
        train = st.form_submit_button("Add Example")

    if train and question and sql:
        vanna_model.train(question=question, sql=sql)
        st.success("✅ Added to training.")

# NL2SQL interface
if st.session_state.get('connected'):
    st.header("Ask Questions")

    user_q = st.text_input("Your question:")
    if st.button("Generate SQL and Execute") and user_q:
        try:
            sql_generated = vanna_model.ask(user_q)
            st.subheader("Generated SQL:")
            st.code(sql_generated, language='sql')

            df_result = vanna_model.run_sql(sql_generated)
            st.dataframe(df_result)
        except Exception as e:
            st.error(f"Error: {e}")
