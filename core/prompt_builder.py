def build_prompt(schema_context, user_question):
    system_prompt = f"""
You are an expert SQL generator for Microsoft SQL Server 2014.
ONLY use provided tables and columns.
No parameters, no variables, no extra comments.
Always output pure SQL.

Schema Context:
{schema_context}

User Question:
{user_question}

SQL:
"""
    return system_prompt
