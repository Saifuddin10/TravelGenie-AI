import ollama
import json

from app.prompts.planner_prompt import build_trip_prompt

def generate_trip_plan(data):

    prompt = build_trip_prompt(data)

    response = ollama.chat(
        model="llama3.2",
        format="json",
        messages=[
            {
                "role" : "user",
                "content": prompt
            }
        ]
    )

    content = response["message"]["content"]

    return json.loads(content)