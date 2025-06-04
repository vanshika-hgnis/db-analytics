# Import python packages
import streamlit as st
import os
from dotenv  import load_dotenv

# ======= BEGIN VANNA SETUP =======
load_dotenv()

from vanna.remote import VannaDefault

KEY = os.getenv("MISTRAL_API_KEY")
vn = VannaDefault(model="mistral-tiny", api_key= KEY)

# vn.connect_to...(YOUR_DATABASE_CREDENTIALS)
# example using suprabase
supra_host= os.getenv("DB_SERVER")
supra_user= os.getenv("DB_USER")
supra_password= os.getenv("DB_PASSWORD")

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


db_name = os.getenv("DB_NAME")
conn_str = build_connection_string(db_name)

vn.connect_to_mssql(odbc_conn_str=conn_str)






# ======= END VANNA SETUP =======

my_question = st.session_state.get("my_question", default=None)

if my_question is None:
    my_question = st.text_input(
        "Ask me a question about your data",
        key="my_question",
    )
else:
    st.text(my_question)
    
    sql = vn.generate_sql(my_question)

    st.text(sql)

    df = vn.run_sql(sql)    
        
    st.dataframe(df, use_container_width=True)

    code = vn.generate_plotly_code(question=my_question, sql=sql, df=df)

    fig = vn.get_plotly_figure(plotly_code=code, df=df)

    st.plotly_chart(fig, use_container_width=True)