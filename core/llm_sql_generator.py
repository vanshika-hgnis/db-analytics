# 

import os
import requests
from dotenv import load_dotenv

load_dotenv()

class LLMSQLGenerator:
    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        self.api_url = "https://api.mistral.ai/v1/chat/completions"
        self.model = os.getenv("MISTRAL_MODEL", "mistral-small-latest")

    def generate(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert SQL generator for Microsoft SQL Server 2014."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }

        response = requests.post(self.api_url, headers=headers, json=data)
        response.raise_for_status()
        content = response.json()
        return content['choices'][0]['message']['content'].strip()
