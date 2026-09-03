from app.utils.itinerary_repair import repair_itinerary


# ============================================================
# TEST INPUT — simulate actual LLM + RAG output
# ============================================================

llm_itinerary = [
    {
        "day": 1,
        "title": "Hyderabad Day 1",
        "activities": [
            {"name": "Charminar"},
            {"name": "Golconda Fort"},
            {"name": "Unknown Place"},
        ],
    },
    {
        "day": 2,
        "title": "Hyderabad Day 2",
        "activities": [
            {"name": "Hussain Sagar"},
            {"name": "Buddha Statue"},
            {"name": "Hussain Sagar"},  # duplicate
        ],
    },
    {
        "day": 3,
        "title": "Hyderabad Day 3",
        "activities": [
            {"name": "Shilparamam"},
            {"name": "Sudha Cars Museum"},
        ],
    },
]


# ============================================================
# SIMULATED RAG DATA
# ============================================================

rag_places = [
    {
        "place": "Charminar",
        "best_time": "Evening",
        "visit_duration": "1 hour",
        "entry_fee": "₹25",
        "timings": "9:30 AM - 5:30 PM",
        "type": "outdoor",
        "ideal_weather": ["clear", "clouds"],
        "nearby_places": ["Golconda Fort"],
    },
    {
        "place": "Golconda Fort",
        "best_time": "Evening",
        "visit_duration": "2 hours",
        "entry_fee": "₹25",
        "timings": "9:00 AM - 5:30 PM",
        "type": "outdoor",
        "ideal_weather": ["clear", "clouds"],
        "nearby_places": ["Charminar"],
    },
    {
        "place": "Hussain Sagar",
        "best_time": "Sunset",
        "visit_duration": "2 hours",
        "entry_fee": "Free",
        "timings": "Open all day",
        "type": "outdoor",
        "ideal_weather": ["clear", "clouds"],
        "nearby_places": ["Buddha Statue"],
    },
    {
        "place": "Buddha Statue",
        "best_time": "Sunset",
        "visit_duration": "1.5 hours",
        "entry_fee": "₹70",
        "timings": "9:00 AM - 9:00 PM",
        "type": "outdoor",
        "ideal_weather": ["clear", "clouds"],
        "nearby_places": ["Hussain Sagar"],
    },
    {
        "place": "Shilparamam",
        "best_time": "Evening",
        "visit_duration": "2 hours",
        "entry_fee": "₹60",
        "timings": "10:30 AM - 8:00 PM",
        "type": "outdoor",
        "ideal_weather": ["clear", "clouds"],
        "nearby_places": [],
    },
    {
        "place": "Sudha Cars Museum",
        "best_time": "Afternoon",
        "visit_duration": "1.5 hours",
        "entry_fee": "₹150",
        "timings": "10:00 AM - 6:00 PM",
        "type": "indoor",
        "ideal_weather": ["rain", "clouds"],
        "nearby_places": [],
    },
    {
        "place": "Salar Jung Museum",
        "best_time": "Morning",
        "visit_duration": "2 hours",
        "entry_fee": "₹50",
        "timings": "10:00 AM - 5:00 PM",
        "type": "indoor",
        "ideal_weather": ["rain", "clouds"],
        "nearby_places": [],
    },
    {
        "place": "Nehru Zoological Park",
        "best_time": "Morning",
        "visit_duration": "3 hours",
        "entry_fee": "₹100",
        "timings": "8:30 AM - 5:00 PM",
        "type": "outdoor",
        "ideal_weather": ["clear", "clouds"],
        "nearby_places": [],
    },
]


weather = {
    "condition": "clear",
    "temperature": 32,
}


# ============================================================
# RUN REPAIR
# ============================================================

print("=" * 60)
print("RUNNING ITINERARY REPAIR INTEGRATION TEST")
print("=" * 60)

repaired = repair_itinerary(
    days=3,
    itinerary=llm_itinerary,
    places=rag_places,
    weather=weather,
)


# ============================================================
# PRINT RESULT
# ============================================================

print("\n" + "=" * 60)
print("FINAL REPAIRED ITINERARY")
print("=" * 60)

for day in repaired:

    print(f"\nDay {day['day']} - {day['title']}")

    for activity in day["activities"]:

        print(
            f"  {activity['name']} | "
            f"{activity['startTime']} - {activity['endTime']} | "
            f"Best: {activity['bestTime']} | "
            f"Duration: {activity['visitDuration']} | "
            f"Fee: {activity['entryFee']}"
        )


# ============================================================
# VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("VALIDATION")
print("=" * 60)

errors = []

all_names = []


for day in repaired:

    activities = day.get("activities", [])

    # --------------------------------------------------------
    # Maximum 3 activities per day
    # --------------------------------------------------------

    if len(activities) > 3:
        errors.append(
            f"Day {day['day']} has more than 3 activities."
        )

    previous_end = None

    for activity in activities:

        name = activity.get("name")

        if not name:
            errors.append(
                f"Day {day['day']} contains activity without a name."
            )
            continue

        all_names.append(name.lower().strip())

        # ----------------------------------------------------
        # Check time fields
        # ----------------------------------------------------

        if not activity.get("startTime"):
            errors.append(
                f"{name} has no startTime."
            )

        if not activity.get("endTime"):
            errors.append(
                f"{name} has no endTime."
            )

        # ----------------------------------------------------
        # Check against RAG
        # ----------------------------------------------------

        rag_match = next(
            (
                place
                for place in rag_places
                if place["place"].lower().strip()
                == name.lower().strip()
            ),
            None,
        )

        if rag_match is None:
            errors.append(
                f"{name} is not present in RAG."
            )
            continue

        # ----------------------------------------------------
        # Verify RAG metadata was used
        # ----------------------------------------------------

        if activity["visitDuration"] != rag_match["visit_duration"]:
            errors.append(
                f"{name}: visit duration does not match RAG."
            )

        if activity["entryFee"] != rag_match["entry_fee"]:
            errors.append(
                f"{name}: entry fee does not match RAG."
            )

        if activity["bestTime"] != rag_match["best_time"]:
            errors.append(
                f"{name}: best time does not match RAG."
            )


# ============================================================
# DUPLICATE CHECK
# ============================================================

duplicates = {
    name
    for name in all_names
    if all_names.count(name) > 1
}

if duplicates:
    errors.append(
        f"Duplicate attractions found: {sorted(duplicates)}"
    )


# ============================================================
# FINAL RESULT
# ============================================================

if errors:

    print("\n❌ VALIDATION FAILED\n")

    for error in errors:
        print("  -", error)

else:

    print("\n✅ VALIDATION PASSED")
    print(
        "Repair output contains valid RAG attractions, "
        "no duplicates, valid metadata, and max 3 activities per day."
    )