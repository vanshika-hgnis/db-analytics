from sql_server import SQLServerConnection

def extract_schema_text():
    db = SQLServerConnection()
    db.connect()

    query = """
    SELECT TABLE_NAME, COLUMN_NAME
    FROM INFORMATION_SCHEMA.COLUMNS
    ORDER BY TABLE_NAME, ORDINAL_POSITION
    """
    df = db.execute_query(query)

    schema_texts = []
    for table in df['TABLE_NAME'].unique():
        columns = df[df['TABLE_NAME'] == table]['COLUMN_NAME'].tolist()
        schema_lines = "\n".join([f"- {col}" for col in columns])
        schema_texts.append(f"Table: {table}\nColumns:\n{schema_lines}")
    
    db.close()
    return schema_texts
