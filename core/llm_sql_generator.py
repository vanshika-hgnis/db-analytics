import ollama
import os
from dotenv import load_dotenv

load_dotenv()

class LLMSQLGenerator:
    def __init__(self):
        self.model = os.getenv("LLM")

    def generate(self, prompt):
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response['message']['content'].strip()
