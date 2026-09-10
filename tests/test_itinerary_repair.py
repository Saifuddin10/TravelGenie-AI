import pytest
from datetime import datetime

from app.utils.itinerary_repair import repair_itinerary


# ============================================================
# SIMULATED LLM OUTPUT
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
            {"name": "Hussain Sagar"},
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
    {
        "place": "Qutub Shahi Tombs",
        "best_time": "Afternoon",
        "visit_duration": "1.5 hours",
        "entry_fee": "₹20",
        "timings": "9:30 AM - 6:00 PM",
        "type": "outdoor",
        "ideal_weather": ["clear", "clouds"],
        "nearby_places": ["Golconda Fort"],
    },
]


# ============================================================
# WEATHER
# ============================================================

weather = {
    "condition": "clear",
    "temperature": 32,
}


# ============================================================
# HELPER
# ============================================================

def time_to_minutes(time_string):
    parsed = datetime.strptime(
        time_string.strip(),
        "%I:%M %p",
    )

    return parsed.hour * 60 + parsed.minute


# ============================================================
# TEST
# ============================================================

def test_itinerary_repair():

    repaired = repair_itinerary(
        days=3,
        itinerary=llm_itinerary,
        places=rag_places,
        weather=weather,
    )

    assert repaired is not None
    assert len(repaired) == 3

    all_names = []

    # ========================================================
    # DAY-BY-DAY VALIDATION
    # ========================================================

    for day in repaired:

        activities = day.get("activities", [])

        # Exactly 3 activities per day
        assert len(activities) == 3, (
            f"Day {day['day']} should have exactly 3 activities, "
            f"but got {len(activities)}."
        )

        previous_end = None

        for activity in activities:

            name = activity.get("name")

            assert name, (
                f"Day {day['day']} contains activity without a name."
            )

            normalized_name = name.lower().strip()
            all_names.append(normalized_name)

            # ------------------------------------------------
            # TIME FIELDS
            # ------------------------------------------------

            start_time = activity.get("startTime")
            end_time = activity.get("endTime")

            assert start_time, f"{name} has no startTime."
            assert end_time, f"{name} has no endTime."

            start_minutes = time_to_minutes(start_time)
            end_minutes = time_to_minutes(end_time)

            # ------------------------------------------------
            # VALID DURATION
            # ------------------------------------------------

            assert end_minutes > start_minutes, (
                f"{name} has invalid timing: "
                f"{start_time} - {end_time}."
            )

            # ------------------------------------------------
            # CHRONOLOGICAL ORDER + 30 MINUTE BUFFER
            # ------------------------------------------------

            if previous_end is not None:

                gap = start_minutes - previous_end

                assert gap >= 30, (
                    f"Day {day['day']}: {name} does not have "
                    f"a 30-minute gap from the previous activity."
                )

            previous_end = end_minutes

            # ------------------------------------------------
            # RAG MATCH
            # ------------------------------------------------

            rag_match = next(
                (
                    place
                    for place in rag_places
                    if place["place"].lower().strip()
                    == normalized_name
                ),
                None,
            )

            assert rag_match is not None, (
                f"{name} is not present in RAG."
            )

            # ------------------------------------------------
            # RAG METADATA
            # ------------------------------------------------

            assert activity.get("visitDuration") == (
                rag_match["visit_duration"]
            ), f"{name}: visit duration does not match RAG."

            assert activity.get("entryFee") == (
                rag_match["entry_fee"]
            ), f"{name}: entry fee does not match RAG."

            assert activity.get("bestTime") == (
                rag_match["best_time"]
            ), f"{name}: best time does not match RAG."

    # ========================================================
    # DUPLICATE CHECK
    # ========================================================

    duplicates = {
        name
        for name in all_names
        if all_names.count(name) > 1
    }

    assert not duplicates, (
        f"Duplicate attractions found: {sorted(duplicates)}"
    )

    # ========================================================
    # TOTAL ACTIVITY COUNT
    # ========================================================

    total_activities = sum(
        len(day.get("activities", []))
        for day in repaired
    )

    expected_activities = 3 * 3

    assert total_activities == expected_activities, (
        f"Expected {expected_activities} total activities, "
        f"but got {total_activities}."
    )