from app.schemas.request import TripRequest

def build_packing_prompt(data: TripRequest):

    return f"""
You are an expert travel packing assistant.

Detination:
{data.destination}

Days:
{data.days}

Preferences:
{data.preferences}

Return ONLY valid JSON.

Return exactly:

{{
    "packing_list":[
        "",
        "",
        ""
    ]
}}

Rules:

- Recommend 10 useful packing items.
- Consider the destination and trip duration.
- Do include explanations.
- Return only JSON.
"""