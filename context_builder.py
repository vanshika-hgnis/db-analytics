# context_builder.py
def build_prompt_context(expanded_tables, table_columns, fk_lines):
    context = "You may ONLY use the following tables and columns:\n\n"
    for table in expanded_tables:
        columns = table_columns.get(table, [])
        column_list = ", ".join([name for name, _ in columns])
        context += f"Table: {table} Columns: {column_list}\n"

    context += "\nForeign Keys:\n"
    context += "\n".join(fk_lines)
    return context
