import ollama
from dotenv import load_dotenv
import os


load_dotenv()

SYSTEM_PROMPT = """
You are a SQL generator for Microsoft SQL Server 2014.
You are provided:
- A database schema (tables, columns, relationships)
- A user question

RULES:
- Only output valid SQL query.
- No explanations, no DDL, no markdown.
- Use only provided tables/columns/relationships.
- Use correct joins based on relationships.

SCHEMA:
{schema_context}

RELATIONSHIPS:
{relationship_context}

EXAMPLES:

Q: List all customers
A: SELECT * FROM CustomerUser;

Q: Show customer name and phone number
A: SELECT CustomerName, PhoneNumber FROM CustomerUser;

Q: List all schedule jobs for customer 'Dynode'
A: 
SELECT sj.*
FROM ScheduleJobs sj
JOIN CustomerUser cu ON sj.CustomerId = cu.Id
WHERE cu.CustomerName = 'Dynode';

Now answer:
{question}

SQL:
"""

class LLMGenerator:
    def __init__(self):
        self.model = os.getenv("LLM")

    def generate_sql(self, schema_context, relationship_context, question):
        prompt = SYSTEM_PROMPT.format(
            schema_context=schema_context,
            relationship_context="\n".join(relationship_context),
            question=question
        )
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response['message']['content'].strip()
