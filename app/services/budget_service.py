from app.prompts.budget_prompt import build_budget_prompt
from app.services.llm_service import LLMService

llm = LLMService()


def generate_budget(data):

    prompt = build_budget_prompt(data)

    response = llm.generate_json(prompt)

    budget = response.get("budget_summary", {})

    hotel = int(budget.get("hotel", 0))
    food = int(budget.get("food", 0))
    transport = int(budget.get("transport", 0))
    activities = int(budget.get("activities", 0))

    total = hotel + food + transport + activities

    if total > data.budget:
        excess = total - data.budget
        activities = max(0, activities - excess)

    remaining = (
        data.budget
        - hotel
        - food
        - transport
        - activities
    )

    return {
        "hotel": hotel,
        "food": food,
        "transport": transport,
        "activities": activities,
        "remaining": remaining
    }