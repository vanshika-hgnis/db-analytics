import ollama
from dotenv import load_dotenv
import os

load_dotenv()


LLM = os.getenv("LLM")


SYSTEM_PROMPT = """
You are a SQL query generator for Microsoft SQL Server 2014.
You are provided:
- A database schema (table names and columns)
- A user question

Rules:
- Only output pure SQL queries.
- Do not output explanations, comments, DDL or markdown.
- Use only the columns listed in schema.
- Do not hallucinate columns/tables.
- If necessary, assume reasonable joins using IDs.

Schema:
{context}

Examples:
Q: List all customers
A: SELECT * FROM CustomerUser;

Q: Show customer name and phone number
A: SELECT CustomerName, PhoneNumber FROM CustomerUser;

Q: List all usernames
A: SELECT Username FROM User;

Now answer:
{question}

SQL:
"""

class LLMGenerator:
    def __init__(self):
        self.model = LLM  # Use larger model if available

    def generate_sql(self, context, question):
        prompt = SYSTEM_PROMPT.format(context=context, question=question)
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response['message']['content'].strip()
