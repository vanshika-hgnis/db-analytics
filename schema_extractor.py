# db-analtics/schema_extractor
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

    schema_lines = []
    for table in df_columns['TABLE_NAME'].unique():
        columns = df_columns[df_columns['TABLE_NAME'] == table]
        col_lines = ", ".join([f"{row['COLUMN_NAME']} ({row['DATA_TYPE']})" for _, row in columns.iterrows()])
        schema_lines.append(f"Table: {table} --> Columns: {col_lines}")

    # FK extraction
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

    fk_lines = []
    for _, row in df_fks.iterrows():
        fk_lines.append(f"{row['ParentTable']}.{row['ParentColumn']} → {row['ReferencedTable']}.{row['ReferencedColumn']}")

    # Sample values
    sample_lines = []
    for table in df_columns['TABLE_NAME'].unique():
        for col in df_columns[df_columns['TABLE_NAME'] == table]['COLUMN_NAME']:
            try:
                sample_query = f"SELECT TOP 3 [{col}] FROM [{table}] WHERE [{col}] IS NOT NULL"
                df_sample = db.execute_query(sample_query)
                values = df_sample[col].tolist()
                if values:
                    sample_lines.append(f"{table}.{col} sample values: {', '.join(str(v) for v in values)}")
            except:
                pass

    db.close()
    # Merge full schema lines
    full_schema = schema_lines + fk_lines + sample_lines
    return full_schema


def build_prompt_context(retrieved_schema):
    context = "Database Schema Context:\n"
    context += "\n".join(retrieved_schema)
    return context
