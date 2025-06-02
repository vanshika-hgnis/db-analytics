from core.sql_server import SQLServerConnection

def extract_full_schema():
    db = SQLServerConnection()
    db.connect()

    query = """
    SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
    FROM INFORMATION_SCHEMA.COLUMNS
    ORDER BY TABLE_NAME, ORDINAL_POSITION
    """
    df = db.execute_query(query)

    schema_docs = []
    for table in df['TABLE_NAME'].unique():
        columns = df[df['TABLE_NAME'] == table]
        col_defs = ", ".join(
            [f"{row['COLUMN_NAME']} ({row['DATA_TYPE']})" for _, row in columns.iterrows()])
        schema_docs.append(f"Table: {table} --> Columns: {col_defs}")

    db.close()
    return schema_docs
