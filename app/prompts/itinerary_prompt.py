def build_itinerary_prompt(data):

    return f"""
You are an expert travel planner.

Return ONLY valid JSON.

Generate EXACTLY {data.days} itinerary objects.

Do NOT include markdown.
Do NOT include explanations.
Do NOT include extra fields.
Do NOT leave titles empty.

Return exactly this JSON:

{{
    "itinerary":[
        {{
            "day":1,
            "title":"Arrival and sightseeing",
            "activities":[
                "Visit Charminar",
                "Explore local markets",
                "Try Hyderabadi Biryani"
            ]
        }}
    ]
}}

Generate EXACTLY {data.days} itinerary objects.
"""