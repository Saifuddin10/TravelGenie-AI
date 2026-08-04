from app.schemas.request import TripRequest


def build_budget_prompt(data: TripRequest):

    return f"""
You are an expert travel budget planner.

Destination:
{data.destination}

Budget:
₹{data.budget}

Travelers:
{data.travelers}

Days:
{data.days}

Return ONLY valid JSON.

Return exactly this format:

{{
    "budget_summary": {{
        "hotel": 0,
        "food": 0,
        "transport": 0,
        "activities": 0
    }}
}}

Rules:

- Return integers only.
- Estimate realistic costs.
- The total should be less than or equal to ₹{data.budget}.
- DO NOT include a "remaining" field.
- DO NOT include explanations.
- Return JSON only.
"""