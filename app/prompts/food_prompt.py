from app.schemas.request import TripRequest

def build_food_prompt(data: TripRequest):

    return f"""
You are an expert food guide.

Destination:
{data.destination}

Return ONLY valid JSON.

Return exactly this format:

{{
    "food_recommendations": [
        {{
            "dish": "",
            "description": "",
            "best_place": "",
            "estimated_cost": 0
        }}
    ]
}}

Rules:

- Recommend 5 famous local dishes.
- Mention a popular place to try each dish.
- estimated_cost must be an integer in INR.
- Return ONLY JSON.
"""