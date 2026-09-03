from app.schemas.request import TripRequest


def build_itinerary_prompt(data: TripRequest, places, weather):
    place_context = "\n".join(
        [
            f"""
Place: {place["place"]}
Description: {place["description"]}
Category: {place["category"]}
Best Time: {place["best_time"]}
Visit Duration: {place["visit_duration"]}
Entry Fee: {place["entry_fee"]}
Timings: {place["timings"]}
Nearby Places: {", ".join(place["nearby_places"]) if isinstance(place["nearby_places"], list) else place["nearby_places"]}
            """.strip()
            for place in places
        ]
    )

    return f"""
You are an expert travel planner.

Your job is to SELECT the best attractions for a realistic day-by-day itinerary.

A separate deterministic scheduler will calculate all startTime and endTime values after your response.

Destination:
{data.destination}

Current Weather:
Temperature: {weather["temperature"]}°C
Condition: {weather["condition"]}
Description: {weather["description"]}

Trip Duration:
{data.days} days

Budget:
₹{data.budget}

Travelers:
{data.travelers}

Preferences:
{data.preferences}

Available Attractions:
{place_context}

TASK

Select attractions for the full trip.

The goal is NOT simply to select popular attractions.
The goal is to create a practical itinerary that can actually be scheduled using the supplied attraction data.

ATTRACTION SELECTION PRIORITY

When choosing attractions, consider the following priorities in order:

1. Traveler preferences and trip requirements.
2. Weather suitability.
3. Best Time suitability.
4. Opening-hour compatibility.
5. Geographic proximity and nearby-place relationships.
6. Reasonable distribution of activities throughout each day.
7. Variety of attraction categories.
8. Avoid unnecessary backtracking or awkward combinations.
9. Avoid attractions that are difficult to schedule together.
10. Avoid selecting attractions only because they appear early in the dataset.

OUTPUT

Return ONLY valid JSON.
Do not include markdown, explanations, comments, or code fences.

Return EXACTLY this structure:

{{
  "itinerary": [
    {{
      "day": 1,
      "title": "",
      "activities": [
        {{
          "name": "",
          "startTime": "",
          "endTime": "",
          "bestTime": "",
          "visitDuration": "",
          "entryFee": ""
        }}
      ]
    }}
  ]
}}

ATTRACTION SELECTION RULES

1. Create exactly {data.days} days.

2. Every day must contain exactly 3 activities.

3. Use ONLY attractions listed in Available Attractions.

4. Never invent an attraction.

5. Do NOT repeat an attraction anywhere in the trip.

6. The "name" must exactly match the attraction's "place" value.

7. Copy "bestTime", "visitDuration", and "entryFee" EXACTLY from the selected attraction.

8. Prefer attractions that can realistically be scheduled within their listed opening hours.

9. Strongly prefer scheduling an attraction during its listed Best Time.

10. Do not intentionally place an attraction far outside its Best Time when another suitable attraction is available.

11. Prefer attractions whose opening hours provide enough flexibility for the deterministic scheduler.

12. Prefer geographically related attractions on the same day when the supplied nearby_places data supports that grouping.

13. Avoid combining attractions that are geographically unrelated when better nearby alternatives are available.

14. Prefer a balanced day rather than selecting three long activities that are difficult to fit together.

15. Prefer a mixture of attraction categories when possible.

16. Consider traveler preferences when deciding between otherwise similar attractions.

17. Consider the current weather when selecting attractions.

18. If weather is Rain, Drizzle, or Thunderstorm:
    - Prefer Indoor attractions.
    - Avoid Outdoor attractions when enough suitable Indoor attractions exist.
    - Do not select Outdoor attractions merely to fill the itinerary if suitable Indoor alternatives are available.

19. If weather is Clear or Clouds:
    - Outdoor attractions may be prioritized.
    - Continue respecting Best Time and opening hours.

20. If temperature is above 35°C:
    - Prefer Morning, Evening, Sunset, or Night outdoor attractions.
    - Prefer Indoor attractions during hotter afternoon periods.
    - Avoid selecting multiple heat-sensitive outdoor attractions for the middle of the day.

21. Do not select attractions whose Best Time is clearly incompatible with their opening hours.

22. Do not select attractions merely because they are free.

23. Do not select attractions merely because they are listed first.

24. Do not use nearby_places as a substitute for selecting an actual attraction.

25. A nearby place may only be selected if that place itself exists in Available Attractions.

SCHEDULING RESPONSIBILITY

The deterministic scheduler is responsible for calculating actual clock times.

Therefore:

- DO NOT calculate startTime.
- DO NOT calculate endTime.
- Return empty strings for startTime and endTime.
- Never invent clock times.
- Do not attempt to simulate the scheduler.

The deterministic scheduler will use the authoritative RAG data to determine:

- opening hours
- Best Time preference
- visit duration
- chronological order
- 30-minute gaps
- no overlapping activities
- valid start and end times

IMPORTANT DATA AUTHORITY

Available Attractions is the only source of truth for attraction details.

Do not modify:

- attraction name
- Best Time
- Visit Duration
- Entry Fee
- Timings

Do not invent missing information.

ACTIVITY FORMAT

For every selected activity return only:

"name": exact attraction name from the dataset
"startTime": ""
"endTime": ""
"bestTime": exact Best Time from the dataset
"visitDuration": exact Visit Duration from the dataset
"entryFee": exact Entry Fee from the dataset

Do NOT return:

- "activity"
- "time"
- "location"
- "description"
- "nearby_places"

FINAL CHECK BEFORE RETURNING

- Exactly {data.days} itinerary days.
- Exactly 3 activities per day.
- No duplicate attractions.
- Every attraction exists in Available Attractions.
- Every attraction's metadata exactly matches the supplied data.
- Attractions should be realistically schedulable.
- Best Time should be respected whenever reasonably possible.
- Weather should influence attraction selection.
- Nearby attractions should be grouped when practical.
- startTime and endTime must be empty strings.
- Return ONLY valid JSON.
"""