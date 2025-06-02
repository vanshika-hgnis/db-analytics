# schema_extractor.py
from sql_server import SQLServerConnection

def extract_full_schema():
    db = SQLServerConnection()
    db.connect()

    column_query = """
    SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
    FROM INFORMATION_SCHEMA.COLUMNS
    ORDER BY TABLE_NAME, ORDINAL_POSITION
    """
    df_columns = db.execute_query(column_query)

    schema_lines, table_columns = [], {}
    for table in df_columns['TABLE_NAME'].unique():
        columns = df_columns[df_columns['TABLE_NAME'] == table]
        col_list = [(row['COLUMN_NAME'], row['DATA_TYPE']) for _, row in columns.iterrows()]
        table_columns[table] = col_list
        col_lines = ", ".join([f"{name} ({dtype})" for name, dtype in col_list])
        schema_lines.append(f"Table: {table} --> Columns: {col_lines}")

    fk_query = """
    SELECT tp.name AS ParentTable, cp.name AS ParentColumn, tr.name AS ReferencedTable, cr.name AS ReferencedColumn
    FROM sys.foreign_keys fk
    INNER JOIN sys.tables tp ON fk.parent_object_id = tp.object_id
    INNER JOIN sys.tables tr ON fk.referenced_object_id = tr.object_id
    INNER JOIN sys.foreign_key_columns fkc ON fkc.constraint_object_id = fk.object_id
    INNER JOIN sys.columns cp ON fkc.parent_object_id = cp.object_id AND fkc.parent_column_id = cp.column_id
    INNER JOIN sys.columns cr ON fkc.referenced_object_id = cr.object_id AND fkc.referenced_column_id = cr.column_id
    """
    df_fks = db.execute_query(fk_query)
    fk_lines = [f"Join Hint: {row['ParentTable']} joins {row['ReferencedTable']} on {row['ParentTable']}.{row['ParentColumn']} = {row['ReferencedTable']}.{row['ReferencedColumn']}" for _, row in df_fks.iterrows()]

    db.close()

    all_tables = list(df_columns['TABLE_NAME'].unique())
    return schema_lines, fk_lines, table_columns, all_tables
