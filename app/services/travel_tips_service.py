from app.prompts.travel_tips_prompt import build_travel_tips_prompt
from app.services.llm_service import LLMService

llm = LLMService()

def generate_travel_tips(data):

    prompt = build_travel_tips_prompt(data)

    response = llm.generate_json(prompt)

    print(response)

    return response