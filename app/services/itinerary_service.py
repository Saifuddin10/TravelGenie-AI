from app.prompts.itinerary_prompt import build_itinerary_prompt
from app.services.llm_service import LLMService

llm = LLMService()

def generate_itinerary(data):

    prompt = build_itinerary_prompt(data)

    response = llm.generate_json(prompt)

    return response["itinerary"] 