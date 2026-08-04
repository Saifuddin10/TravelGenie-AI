from app.prompts.budget_prompt import build_budget_prompt
from app.services.llm_service import LLMService
from app.validators.budget_validator import validate_budget

llm = LLMService()

def generate_budget(data):

    prompt = build_budget_prompt(data)

    response = llm.generate_json(prompt)

    budget = response["budget_summary"]

    budget = validate_budget(data.budget, budget)

    return budget