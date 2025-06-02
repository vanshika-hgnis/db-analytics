import ollama
import os
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """
You are an expert SQL generator for Microsoft SQL Server 2014.

You are given:
- The database schema context
- The user question

Your job is to generate full valid SQL queries for Microsoft SQL Server 2014.

Only output the SQL query. Do not explain anything.

{context}

USER QUESTION:
{question}

SQL:
"""

class LLMSQLGenerator:
    def __init__(self):
        self.model = os.getenv("LLM")  # e.g., phi3:3.8b

    def generate_sql(self, full_context, question):
        prompt = SYSTEM_PROMPT.format(context=full_context, question=question)
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response['message']['content'].strip()
