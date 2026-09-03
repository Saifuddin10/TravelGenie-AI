from app.schemas.request import TripRequest

def build_packing_prompt(data: TripRequest):

    return f"""
You are an expert travel packing assistant.

Destination: {data.destination}
Days: {data.days}
Preferences: {data.preferences}

Return ONLY valid JSON.

Return exactly:

{{
    "packing_list": [
        {{
            "item": "",
            "reason": ""
        }}
    ]
}}

Rules:
- Recommend exactly 10 packing items.
- Each packing item MUST be an object.
- Never return an array of strings.
- Include one short reason for each item.
- Consider destination, duration and preferences.
- Return only JSON.
- No markdown.
- No explanations outside the JSON.
"""