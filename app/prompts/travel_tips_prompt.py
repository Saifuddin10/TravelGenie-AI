from app.schemas.request import TripRequest

def build_travel_tips_prompt(data: TripRequest):

    return f"""
You are an expert travel advisor.

Destination: {data.destination}
Days: {data.days}
Budget: ₹{data.budget}
Preferences: {data.preferences}

Return ONLY valid JSON.

Return exactly:

{{
    "travel_tips": [
        "Tip 1",
        "Tip 2",
        "Tip 3",
        "Tip 4",
        "Tip 5"
    ]
}}

Rules:
- Return exactly 5 travel tips.
- Tips must be specific to {data.destination}.
- Include safety, transport, local customs, weather and money-saving advice.
- Return only the JSON shown above.
- No markdown.
- No explanations.
"""