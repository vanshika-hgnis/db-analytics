# streamlit_app.py

import streamlit as st

from sql_server import SQLServerConnection
from schema_extractor import extract_full_schema
from vector_store import VectorStore
from table_detector import detect_relevant_tables
from fk_graph_builder import build_fk_graph
from table_expander import expand_tables
from context_builder import build_prompt_context
from join_controller import should_use_joins
from llm_sql_generator import LLMSQLGenerator
from sql_validator import SQLValidator
from codeblock_cleaner import clean_llm_sql

st.set_page_config(page_title="Vanna Clone V12.0", layout="wide")
st.title("🧠 Vanna Clone V12.0 — Natural Language SQL Agent")

# Connect to DB
db = SQLServerConnection()
connected = db.connect()
if not connected:
    st.error("❌ Failed to connect to SQL Server.")
    st.stop()

# Extract schema once
schema_lines, fk_lines, table_columns, all_tables = extract_full_schema()

# Build FK Graph once
fk_graph = build_fk_graph(fk_lines)

# Build VectorStore (no change)
db_name = db.connection.getinfo(6)
vector_store = VectorStore(db_name)
vector_store.build_store(schema_lines)

# Initialize models
llm = LLMSQLGenerator()
validator = SQLValidator()

# Streamlit UI
user_question = st.text_area("Ask your natural language SQL question:")

if st.button("Generate & Execute"):
    detected_tables = detect_relevant_tables(user_question, all_tables)
    expanded_tables = expand_tables(detected_tables, fk_graph, max_depth=1)

    if not expanded_tables:
        st.warning("⚠ No tables detected from your input.")
        st.stop()

    # If simple single-table query, avoid LLM entirely:
    if not should_use_joins(expanded_tables):
        selected_table = expanded_tables[0]
        final_sql = f"SELECT * FROM {selected_table}"
    else:
        # Build prompt for multi-table join
        prompt_context = build_prompt_context(expanded_tables, table_columns, fk_lines)
        generated_sql = llm.generate_sql(prompt_context, user_question)
        cleaned_sql = clean_llm_sql(generated_sql)
        final_sql = cleaned_sql

    st.subheader("Generated SQL")
    st.code(final_sql, language='sql')

    valid = validator.validate(final_sql)
    if not valid:
        st.warning("⚠ SQL parse failed, execution aborted.")
        st.stop()

    try:
        df = db.execute_query(final_sql)
        st.success("✅ Query executed successfully!")
        st.dataframe(df)
    except Exception as e:
        st.error(f"❌ Execution failed: {str(e)}")

if st.button("Close DB Connection"):
    db.close()
    st.success("SQL Server connection closed.")
