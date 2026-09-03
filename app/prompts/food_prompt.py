from app.schemas.request import TripRequest

def build_food_prompt(data: TripRequest, foods):

    food_context = "\n".join(
        [
            f"""
Dish: {food["dish"]}
Restaurant: {food["restaurant"]}
Category: {food["category"]}
Price: {food["price"]}
Description: {food["description"]}
""".strip()
            for food in foods
        ]
    )

    return f"""
You are an expert local food guide.

Destination:
{data.destination}

Available Food Recommendatins:
{food_context}

Return ONLY valid JSON.

Return exactly this format:

{{
    "food_recommendations": [
        {{
            "dish": "",
            "description": "",
            "best_place": "",
            "estimated_price": 0
        }}
    ]
}}

IMPORTANT RULES

- Recommend exactly 5 food items.
- Use ONLY the dishes listed above.
- Use ONLY the restaurants listed above.
- Copy the description from the provided data if appropriate.
- "best_place" must exactly match the restaurant name from the data.
- "estimated_price" should be the price provided in the data.
- Do NOT invent dishes.
- Do NOT invent restaurants.
- Return valid JSON only.
- No markdown.
- No explanations.
"""