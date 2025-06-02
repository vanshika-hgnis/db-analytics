# llm_sql_generator.py
import ollama
import os
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """
You are a professional SQL generator for Microsoft SQL Server 2014.

You are provided:
- Allowed tables and columns
- Foreign key join hints
- The user question

STRICT RULES:
- Only use provided tables and columns.
- DO NOT hallucinate parameter placeholders or variables like @Id or @DynodeId.
- Use literal string values exactly as mentioned in user question.
- Do not create parameterized SQL queries.
- If multiple tables are provided, follow FK join hints.
- If only one table is provided, generate simple SELECT * FROM that table.
- Always output only pure SQL.
- NEVER add explanation or comments.

{context}

USER QUESTION:
{question}

SQL:
"""

class LLMSQLGenerator:
    def __init__(self):
        self.model = os.getenv("LLM")  # Example: phi3:3.8b

    def generate_sql(self, full_context, question):
        prompt = SYSTEM_PROMPT.format(context=full_context, question=question)
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response['message']['content'].strip()
