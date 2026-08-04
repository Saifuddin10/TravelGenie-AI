from app.prompts.food_prompt import build_food_prompt
from app.services.llm_service import LLMService

llm = LLMService()

def generate_food(data):

    prompt = build_food_prompt(data)

    response = llm.generate_json(prompt)

    return response["food_recommendations"]