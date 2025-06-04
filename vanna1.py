import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
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

# Initialize VannaRemote model
if "vanna_model" not in st.session_state:

    vn = VannaDefault(
        model=os.getenv("VANNA_MODEL_NAME"), 
        api_key=os.getenv("VANNA_API_KEY"),
        email=os.getenv("VANNA_EMAIL")
    )

    st.session_state.vanna_model = vn

# Streamlit UI setup
st.set_page_config(page_title="DB Analytics", layout="wide")
st.title("🧠 DB Analytics")

# Sidebar DB Connection Form
with st.sidebar.form("db_form"):
    db_name = st.text_input("Enter Database Name:", value=st.session_state.get("db_name", ""))
    submit = st.form_submit_button("Connect & Train")

if submit:
    try:
        conn_str = build_connection_string(db_name)
        st.session_state.conn_str = conn_str
        st.session_state.db_name = db_name

        # Connect to your database via Vanna Remote
        st.session_state.vanna_model.connect_to_mssql(odbc_conn_str=conn_str)

        # Train embeddings if not already trained
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

# Main Query Interface
if st.session_state.get("ready", False):
    st.header("💬 Ask Your Database")

    user_q = st.text_input("Ask your question:")

    if st.button("Ask & Run") and user_q:
        try:
            sql = st.session_state.vanna_model.generate_sql(user_q)
            st.subheader("Generated SQL:")
            st.code(sql, language='sql')

            df = st.session_state.vanna_model.run_sql(sql)
            st.subheader("Query Results:")
            st.dataframe(df)

            plotly_code = st.session_state.vanna_model.generate_plotly_code(question=user_q, sql=sql, df=df)
            fig = st.session_state.vanna_model.get_plotly_figure(plotly_code=plotly_code, df=df)

            if fig:
                st.subheader("Chart:")
                st.plotly_chart(fig)

        except Exception as e:
            st.error(f"❌ Error: {e}")
