import ollama
import os
from dotenv import load_dotenv


SYSTEM_PROMPT = """
You are a SQL generator for Microsoft SQL Server 2014.
You are provided:
- Schema (tables and columns)
- Foreign key relationships
- Join path hints (how to link tables)
- Sample values (data examples)
- User question

RULES:
- Generate valid SQL queries.
- Use joins based on join path hints.
- Use sample values to match entities.
- Do NOT reference columns across tables without proper joins.
- Do NOT hallucinate any field not present in schema.

SCHEMA:
{schema_context}

RELATIONSHIPS:
{relationship_context}

JOIN PATH HINTS:
{join_path_context}

SAMPLE VALUES:
{value_context}

EXAMPLES:

Q: List all customers
A: SELECT * FROM CustomerUser;

Q: List all schedule jobs for customer 'Dynode'
A:
SELECT sj.*
FROM ScheduleJobs sj
JOIN CustomerUser cu ON sj.CustomerId = cu.Id
WHERE cu.CustomerName = 'Dynode';

USER QUESTION:
{question}

SQL:
"""

class LLMGenerator:
    def __init__(self):
        self.model = os.getenv("LLM")

    def generate_sql(self, schema_context, relationship_context, join_path_context, value_context, question):
        prompt = SYSTEM_PROMPT.format(
            schema_context=schema_context,
            relationship_context="\n".join(relationship_context),
            join_path_context="\n".join(join_path_context),
            value_context="\n".join(value_context),
            question=question
        )
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response['message']['content'].strip()
