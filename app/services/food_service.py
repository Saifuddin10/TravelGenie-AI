from app.prompts.food_prompt import build_food_prompt
from app.services.llm_service import LLMService
from app.food_rag.retriever import retrieve_food

llm = LLMService()

def generate_food(data):

    foods = retrieve_food(data.destination)

    print("\nRetrived foods")
    print(foods)

    prompt = build_food_prompt(data, foods)

    response = llm.generate_json(prompt)

    print("\nFood LLM Response:")
    print(response)

    # food = response.get("food_recommendations", [])

    # for item in food:

    #     if "estimated_price" not in item:
    #         item["estimated_price"] = (
    #             item.pop("estimated_cost", None)
    #             or item.pop("price", None)
    #             or 200
    #         )

    return response["food_recommendations"]