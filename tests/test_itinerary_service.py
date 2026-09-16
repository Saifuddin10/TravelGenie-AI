from datetime import datetime
from types import SimpleNamespace

from app.services import itinerary_service


# ============================================================
# TEST INPUT
# ============================================================

data = SimpleNamespace(
    destination="Hyderabad",
    days=3,
    budget=10000,
    travelers=2,
    preferences="sightseeing, food, night life",
)

weather = {
    "condition": "clear",
    "description": "Clear sky",
    "temperature": 32,
}


# ============================================================
# SIMULATED RAG DATA
# ============================================================

rag_places = [
    {
        "place": "Charminar",
        "description": "Historic monument and iconic landmark of Hyderabad.",
        "category": "tourist attraction",
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
        "description": "Historic fort known for its architecture and panoramic views.",
        "category": "historical",
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
        "description": "Large lake in Hyderabad known for its scenic views and boating.",
        "category": "lake",
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
        "description": "Large Buddha statue located on an island in Hussain Sagar Lake.",
        "category": "landmark",
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
        "description": "Traditional arts and crafts village showcasing Indian culture.",
        "category": "cultural",
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
        "description": "Unique museum displaying unusual and handmade cars.",
        "category": "museum",
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
        "description": "Museum featuring a large collection of art, antiques, and artifacts.",
        "category": "museum",
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
        "description": "Large zoological park with diverse animals and outdoor exhibits.",
        "category": "zoo",
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
        "description": "Historic tomb complex featuring Indo-Islamic architecture.",
        "category": "historical",
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
# SIMULATED LLM OUTPUT
# ============================================================

llm_response = {
    "itinerary": [
        {
            "day": 1,
            "title": "Hyderabad Day 1",
            "activities": [
                {"name": "Charminar"},
                {"name": "Golconda Fort"},
                {"name": "Hussain Sagar"},
            ],
        },
        {
            "day": 2,
            "title": "Hyderabad Day 2",
            "activities": [
                {"name": "Buddha Statue"},
                {"name": "Shilparamam"},
                {"name": "Sudha Cars Museum"},
            ],
        },
        {
            "day": 3,
            "title": "Hyderabad Day 3",
            "activities": [
                {"name": "Salar Jung Museum"},
                {"name": "Nehru Zoological Park"},
                {"name": "Qutub Shahi Tombs"},
            ],
        },
    ]
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

def test_generate_itinerary(monkeypatch):

    # --------------------------------------------------------
    # Mock RAG retrieval
    # --------------------------------------------------------

    monkeypatch.setattr(
        itinerary_service,
        "retrieve_places",
        lambda destination: rag_places,
    )

    # --------------------------------------------------------
    # Mock weather filtering
    # --------------------------------------------------------

    monkeypatch.setattr(
        itinerary_service,
        "filter_places_by_weather",
        lambda places, weather: places,
    )

    # --------------------------------------------------------
    # Mock LLM response
    # --------------------------------------------------------

    monkeypatch.setattr(
        itinerary_service.llm,
        "generate_json",
        lambda prompt: llm_response,
    )

    # --------------------------------------------------------
    # Generate itinerary
    # --------------------------------------------------------

    itinerary = itinerary_service.generate_itinerary(
        data=data,
        weather=weather,
    )

    # ========================================================
    # BASIC VALIDATION
    # ========================================================

    assert itinerary is not None
    assert isinstance(itinerary, list)

    assert len(itinerary) == data.days, (
        f"Expected {data.days} days, "
        f"but got {len(itinerary)}."
    )

    # ========================================================
    # DAY-BY-DAY VALIDATION
    # ========================================================

    all_names = []

    for day in itinerary:

        activities = day.get("activities", [])

        assert len(activities) == 3, (
            f"Day {day.get('day')} should have exactly "
            f"3 activities, but got {len(activities)}."
        )

        previous_end = None

        for activity in activities:

            # ------------------------------------------------
            # REQUIRED NAME
            # ------------------------------------------------

            name = activity.get("name")

            assert name, (
                f"Day {day.get('day')} contains "
                f"activity without a name."
            )

            all_names.append(name.lower().strip())

            # ------------------------------------------------
            # REQUIRED TIME FIELDS
            # ------------------------------------------------

            start_time = activity.get("startTime")
            end_time = activity.get("endTime")

            assert start_time, (
                f"{name} has no startTime."
            )

            assert end_time, (
                f"{name} has no endTime."
            )

            # ------------------------------------------------
            # VALID TIME FORMAT
            # ------------------------------------------------

            start_minutes = time_to_minutes(start_time)
            end_minutes = time_to_minutes(end_time)

            # ------------------------------------------------
            # VALID ACTIVITY DURATION
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
                    f"Day {day.get('day')}: {name} does not "
                    f"have a 30-minute gap from the previous "
                    f"activity."
                )

            previous_end = end_minutes

            # ------------------------------------------------
            # REQUIRED METADATA
            # ------------------------------------------------

            assert activity.get("visitDuration"), (
                f"{name} has no visitDuration."
            )

            assert activity.get("entryFee") is not None, (
                f"{name} has no entryFee."
            )

            assert activity.get("bestTime"), (
                f"{name} has no bestTime."
            )

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
        for day in itinerary
    )

    expected_activities = 3 * data.days

    assert total_activities == expected_activities, (
        f"Expected {expected_activities} total activities, "
        f"but got {total_activities}."
    )