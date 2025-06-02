# codeblock_cleaner.py
def clean_llm_sql(raw_sql):
    raw_sql = raw_sql.strip()
    if raw_sql.startswith("```sql"):
        raw_sql = raw_sql[6:]
    if raw_sql.endswith("```"):
        raw_sql = raw_sql[:-3]
    return raw_sql.strip()
