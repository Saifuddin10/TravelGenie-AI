from app.prompts.packing_prompt import build_packing_prompt
from app.services.llm_service import LLMService

llm = LLMService()

def generate_packing(data):

    prompt = build_packing_prompt(data)

    response = llm.generate_json(prompt)

    return response["packing_list"]