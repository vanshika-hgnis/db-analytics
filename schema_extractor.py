from sql_server import SQLServerConnection

def extract_schema_and_data():
    db = SQLServerConnection()
    db.connect()

    # Extract Columns
    column_query = """
    SELECT TABLE_NAME, COLUMN_NAME
    FROM INFORMATION_SCHEMA.COLUMNS
    ORDER BY TABLE_NAME, ORDINAL_POSITION
    """
    df_columns = db.execute_query(column_query)

    schema_texts = []
    for table in df_columns['TABLE_NAME'].unique():
        columns = df_columns[df_columns['TABLE_NAME'] == table]['COLUMN_NAME'].tolist()
        schema_lines = "\n".join([f"- {col}" for col in columns])
        schema_texts.append(f"Table: {table}\nColumns:\n{schema_lines}")

    # Extract Foreign Keys
    fk_query = """
    SELECT
        tp.name AS ParentTable,
        cp.name AS ParentColumn,
        tr.name AS ReferencedTable,
        cr.name AS ReferencedColumn
    FROM sys.foreign_keys fk
    INNER JOIN sys.tables tp ON fk.parent_object_id = tp.object_id
    INNER JOIN sys.tables tr ON fk.referenced_object_id = tr.object_id
    INNER JOIN sys.foreign_key_columns fkc ON fkc.constraint_object_id = fk.object_id
    INNER JOIN sys.columns cp ON fkc.parent_object_id = cp.object_id AND fkc.parent_column_id = cp.column_id
    INNER JOIN sys.columns cr ON fkc.referenced_object_id = cr.object_id AND fkc.referenced_column_id = cr.column_id
    """
    df_fks = db.execute_query(fk_query)

    fk_texts = []
    for _, row in df_fks.iterrows():
        fk_texts.append(f"{row['ParentTable']}.{row['ParentColumn']} → {row['ReferencedTable']}.{row['ReferencedColumn']}")

    # Build Join Path Hints
    join_path_texts = []
    for fk in fk_texts:
        parent, referenced = fk.split(" → ")
        p_table, p_col = parent.split(".")
        r_table, r_col = referenced.split(".")
        join_path_texts.append(f"To join {p_table} and {r_table}, use: {p_table}.{p_col} = {r_table}.{r_col}")

    # Extract Sample Data
    value_texts = []
    for table in df_columns['TABLE_NAME'].unique():
        for col in df_columns[df_columns['TABLE_NAME'] == table]['COLUMN_NAME']:
            if col.lower() in ['customername', 'username', 'name']:
                try:
                    query = f"SELECT TOP 5 [{col}] FROM [{table}] WHERE [{col}] IS NOT NULL"
                    df_sample = db.execute_query(query)
                    values = df_sample[col].tolist()
                    if values:
                        value_texts.append(f"{table}.{col} sample values: {', '.join(str(v) for v in values)}")
                except Exception as e:
                    continue

    db.close()
    return schema_texts, fk_texts, join_path_texts, value_texts
