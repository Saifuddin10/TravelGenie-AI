import json
import ollama


class LLMService:

    def __init__(self, model="llama3.2"):
        self.model = model

    def generate_json(self, prompt: str):

        response = ollama.chat(
            model=self.model,
            format="json",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return json.loads(response["message"]["content"])