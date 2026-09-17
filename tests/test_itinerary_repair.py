import pytest
from datetime import datetime

from app.utils.itinerary_repair import repair_itinerary, _get_nearby_places, _nearby_score, _select_best_fallback


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

def test_get_nearby_places_normalize_values():

    place = {
        "place": "Charminar",
        "nearby_places":[
            "Mecca Masjid",
            "Laad Bazaar"
        ],
    }

    result = _get_nearby_places(place)

    assert result == {
        "mecca masjid",
        "laad bazaar"
    }

def test_get_nearby_places_handles_empty_values():

    place = {
        "place": "Charminar",
        "nearby_places": "None",
    }

    result = _get_nearby_places(place)

    assert result == set()

def test_nearby_score_candidate_points_to_selected():

    candidate = {
        "place": "Mecca Masjid",
        "nearby_places": ["Charminar"],
    }

    selected = [
        {
            "place": "Charminar",
            "nearby_places": [],
        }
    ]

    score = _nearby_score(
        candidate,
        selected,
    )

    assert score == 25

def test_nearby_score_selected_points_to_candidate():

    candidate = {
        "place": "Mecca Masjid",
        "nearby_places": [],
    }

    selected = [
        {
            "place": "Charminar",
            "nearby_places": ["Mecca Masjid"],
        }
    ]

    score = _nearby_score(
        candidate,
        selected,
    )

    assert score == 25

def test_nearby_score_bidirectional_relationship():

    candidate = {
        "place": "Mecca Masjid",
        "nearby_places": ["Charminar"],
    }

    selected = [
        {
            "place": "Charminar",
            "nearby_places": ["Mecca Masjid"]
        }
    ]

    score = _nearby_score(
        candidate,
        selected,
    )

    assert score == 50

def test_nearby_score_unrelated_place():

    candidate = {
        "place": "Golkonda Fort",
        "nearby_places": ["Qutub Shahi Tombs"],
    }

    selected = [
        {
            "place": "Charminar",
            "nearby_places": ["Mecca Masjid", "Laad Bazaar"],
        }
    ]

    score = _nearby_score(
        candidate,
        selected
    )

    assert score == 0

def test_select_best_fallback_prefers_nearby_place():

    selected_activity = {
        "name": "Charminar",
        "_start_minutes": 9 * 60,
        "_end_minutes": 11 * 60,
    }

    selected_place = {
        "place": "Charminar",
        "nearby_places": ["Mecca Masjid"],
    }

    nearby_candidate = {
        "place": "Mecca Masjid",
        "nearby_places": ["Charminar"],
        "best_time": "Morning",
        "visit_duration": "1 hour",
        "timings": "4 AM - 9:30 PM",
        "entry_fee": "Free",
        "ideal_weather": ["clear"],
        "type": "outdoor",
    }

    unrelated_candidate = {
        "place": "Golkonda Fort",
        "nearby_places": ["Qutub Shahi Tombs"],
        "best_time": "Morning",
        "visit_duration": "1 hour",
        "timings": "9 AM - 5:30 PM",
        "entry_fee": "₹40",
        "ideal_weather": ["clear"],
        "type": "outdoor",
    }

    place, activity = _select_best_fallback(
        remaining_places=[
            unrelated_candidate,
            nearby_candidate,
        ],
        existing_activities=[
            selected_activity,
            selected_place,
        ],
        weather={
            "condition": "clear",
            "temperature": 28,
        },
    )

    assert place["place"] == "Mecca Masjid"
    assert activity["name"] == "Mecca Masjid"

def test_repair_itinerary_groups_nearby_attractions():

    places = [
        {
            "place": "Charminar",
            "nearby_places": ["Mecca Masjid", "Laad Bazaar"],
            "best_time": "Morning",
            "visit_duration": "2 hours",
            "timings": "9:30 AM - 5:30 PM",
            "entry_fee": "₹25",
            "ideal_weather": ["clear"],
            "type": "outdoor",
        },
        {
            "place": "Mecca Masjid",
            "nearby_places": ["Charminar", "Laad Bazaar"],
            "best_time": "Morning",
            "visit_duration": "1 hour",
            "timings": "4 AM - 9:30 PM",
            "entry_fee": "Free",
            "ideal_weather": ["clear"],
            "type": "outdoor",
        },
        {
            "place": "Laad Bazaar",
            "nearby_places": ["Charminar", "Mecca Masjid"],
            "best_time": "Evening",
            "visit_duration": "2 hours",
            "timings": "10 AM - 10 PM",
            "entry_fee": "Free",
            "ideal_weather": ["clear"],
            "type": "outdoor",
        },
        {
            "place": "Golkonda Fort",
            "nearby_places": ["Qutub Shahi Tombs"],
            "best_time": "Evening",
            "visit_duration": "3 hours",
            "timings": "9 AM - 5:30 PM",
            "entry_fee": "₹40",
            "ideal_weather": ["clear"],
            "type": "outdoor",
        },
    ]

    itinerary = [
        {
            "day": 1,
            "title": "Day 1",
            "activities": [
                {
                    "name": "Charminar"
                }
            ]
        }
    ]

    repaired = repair_itinerary(
        days=1,
        itinerary=itinerary,
        places=places,
        weather={
            "condition": "clear",
            "temperature": 28,
        },
    )

    activities = repaired[0]["activities"]

    assert len(activities) == 3

    names = [
        activity["name"]
        for activity in activities
    ]

    assert "Charminar" in names
    assert "Mecca Masjid" in names
    assert "Laad Bazaar" in names

def test_select_best_fallback_rejects_infeasible_nearby_place():

    selected_activity = {
        "name": "Charminar",
        "_start_minutes": 9 * 60,
        "_end_minutes": 11 * 60,
    }

    selected_place = {
        "place": "Charminar",
        "nearby_places": ["Mecca Masjid"],
    }

    nearby_but_infeasible = {
        "place": "Mecca Masjid",
        "nearby_places": ["Charminar"],
        "best_time": "Morning",
        "visit_duration": "2 hours",
        "timings": "10 AM - 11 AM",
        "entry_fee": "Free",
        "ideal_weather": ["clear"],
        "type": "outdoor",
    }

    feasible_unrelated = {
        "place": "Golkonda Fort",
        "nearby_places": ["Qutub Shahi Tombs"],
        "best_time": "Morning",
        "visit_duration": "1 hour",
        "timings": "9 AM - 5:30 PM",
        "entry_fee": "₹40",
        "ideal_weather": ["clear"],
        "type": "outdoor",
    }

    place, activity = _select_best_fallback(
        remaining_places=[
            nearby_but_infeasible,
            feasible_unrelated,
        ],
        existing_activities=[
            selected_activity,
            selected_place,
        ],
        weather={
            "condition": "clear",
            "temperature": 28,
        },
    )

    assert place["place"] == "Golkonda Fort"
    assert activity["name"] == "Golkonda Fort"

def test_repair_itinerary_does_not_duplicate_nearby_attractions_across_days():

    places = [
        {
            "place": "Charminar",
            "nearby_places": ["Mecca Masjid", "Laad Bazaar"],
            "best_time": "Morning",
            "visit_duration": "2 hours",
            "timings": "9:30 AM - 5:30 PM",
            "entry_fee": "₹25",
            "ideal_weather": ["clear"],
            "type": "outdoor",
        },
        {
            "place": "Mecca Masjid",
            "nearby_places": ["Charminar", "Laad Bazaar"],
            "best_time": "Morning",
            "visit_duration": "1 hour",
            "timings": "4 AM - 9:30 PM",
            "entry_fee": "Free",
            "ideal_weather": ["clear"],
            "type": "outdoor",
        },
        {
            "place": "Laad Bazaar",
            "nearby_places": ["Charminar", "Mecca Masjid"],
            "best_time": "Evening",
            "visit_duration": "2 hours",
            "timings": "10 AM - 10 PM",
            "entry_fee": "Free",
            "ideal_weather": ["clear"],
            "type": "outdoor",
        },
        {
            "place": "Golkonda Fort",
            "nearby_places": ["Qutub Shahi Tombs"],
            "best_time": "Evening",
            "visit_duration": "3 hours",
            "timings": "9 AM - 5:30 PM",
            "entry_fee": "₹40",
            "ideal_weather": ["clear"],
            "type": "outdoor",
        },
        {
            "place": "Qutub Shahi Tombs",
            "nearby_places": ["Golkonda Fort"],
            "best_time": "Morning",
            "visit_duration": "2 hours",
            "timings": "9:30 AM - 5:30 PM",
            "entry_fee": "₹20",
            "ideal_weather": ["clear"],
            "type": "outdoor",
        },
        {
            "place": "Birla Mandir",
            "nearby_places": ["Lumbini Park", "Hussain Sagar"],
            "best_time": "Evening",
            "visit_duration": "1 hour",
            "timings": "7 AM - 9 PM",
            "entry_fee": "Free",
            "ideal_weather": ["clear"],
            "type": "outdoor",
        },
    ]

    itinerary = [
        {
            "day": 1,
            "title": "Day 1",
            "activities": [
                {"name": "Charminar"},
                {"name": "Mecca Masjid"},
            ],
        },
        {
            "day": 2,
            "title": "Day 2",
            "activities": [
                {"name": "Golkonda Fort"},
            ],
        },
    ]

    repaired = repair_itinerary(
        days=2,
        itinerary=itinerary,
        places=places,
        weather={
            "condition": "clear",
            "temperature": 28,
        },
    )

    day_1_names = {
        activity["name"]
        for activity in repaired[0]["activities"]
    }

    day_2_names = {
        activity["name"]
        for activity in repaired[1]["activities"]
    }

    all_names = day_1_names | day_2_names

    assert len(all_names) == (
        len(day_1_names) + len(day_2_names)
    )

    assert "Charminar" in day_1_names
    assert "Mecca Masjid" in day_1_names
    assert "Golkonda Fort" in day_2_names

def test_repair_itinerary_handles_malformed_llm_activities():

    places = [
        {
            "place": "Charminar",
            "nearby_places": [],
            "best_time": "Morning",
            "visit_duration": "2 hours",
            "timings": "9:30 AM - 5:30 PM",
            "entry_fee": "₹25",
            "ideal_weather": ["clear"],
            "type": "outdoor",
        },
        {
            "place": "Mecca Masjid",
            "nearby_places": ["Charminar"],
            "best_time": "Morning",
            "visit_duration": "1 hour",
            "timings": "4 AM - 9:30 PM",
            "entry_fee": "Free",
            "ideal_weather": ["clear"],
            "type": "outdoor",
        },
        {
            "place": "Laad Bazaar",
            "nearby_places": ["Charminar", "Mecca Masjid"],
            "best_time": "Evening",
            "visit_duration": "2 hours",
            "timings": "10 AM - 10 PM",
            "entry_fee": "Free",
            "ideal_weather": ["clear"],
            "type": "outdoor",
        },
        {
            "place": "Golkonda Fort",
            "nearby_places": [],
            "best_time": "Evening",
            "visit_duration": "3 hours",
            "timings": "9 AM - 5:30 PM",
            "entry_fee": "₹40",
            "ideal_weather": ["clear"],
            "type": "outdoor",
        },
    ]

    malformed_itinerary = [
        {
            "day": 1,
            "title": "Day 1",
            "activities": [
                {"name": "Charminar"},
                {"activity": "Mecca Masjid"},
                {},
                None,
                {"name": "Unknown Place"},
            ],
        }
    ]

    repaired = repair_itinerary(
        days=1,
        itinerary=malformed_itinerary,
        places=places,
        weather={
            "condition": "clear",
            "temperature": 28,
        },
    )

    activities = repaired[0]["activities"]

    assert len(activities) == 3

    names = [
        activity["name"]
        for activity in activities
    ]

    assert "Charminar" in names
    assert "Mecca Masjid" in names

    # Invalid LLM entries should not appear.
    assert "Unknown Place" not in names

    # Every returned activity must come from RAG.
    rag_names = {
        place["place"]
        for place in places
    }

    assert set(names).issubset(rag_names)

def test_repair_itinerary_replaces_unschedulable_valid_llm_activity():

    places = [
        {
            "place": "Charminar",
            "nearby_places": [],
            "best_time": "Morning",
            "visit_duration": "2 hours",
            "timings": "9:30 AM - 5:30 PM",
            "entry_fee": "₹25",
            "ideal_weather": ["clear"],
            "type": "outdoor",
        },
        {
            "place": "Mecca Masjid",
            "nearby_places": [],
            "best_time": "Morning",
            "visit_duration": "1 hour",
            "timings": "4 AM - 9:30 PM",
            "entry_fee": "Free",
            "ideal_weather":["clear"],
            "type": "outdoor",
        },
        {
            "place": "Laad Bazaar",
            "nearby_places": [],
            "best_time": "Evening",
            "visit_duration": "2 hours",
            "timings": "10 AM - 10 PM",
            "entry_fee": "Free",
            "ideal_weather":["clear"],
            "type": "outdoor",
        },
        {
            "place": "Golkonda Fort",
            "nearby_places": [],
            "best_time": "Evening",
            "visit_duration": "3 hour",
            "timings": "9 AM - 5:30 PM",
            "entry_fee": "₹40",
            "ideal_weather":["clear"],
            "type": "outdoor",
        },
    ]

    itinerary = [
        {
            "day": 1,
            "title": "Day 1",
            "activities": [
                {"name": "Charminar"},
                {"name": "Golkonda Fort"},
                {"name": "Laad Bazaar"},
            ],
        }
    ]

    repaired = repair_itinerary(
        days=1,
        itinerary=itinerary,
        places=places,
        weather={
            "condition": "clear",
            "temperature": 28,
        },
    )

    activities = repaired[0]["activities"]

    assert len(activities) == 3

    names = [
        activity["name"]
        for activity in activities
    ]

    assert len(names) == len(set(names))

    rag_names = {
        place["place"]
        for place in places
    }

    assert set(names).issubset(rag_names)

    for activity in activities:

        start = time_to_minutes(activity["startTime"])
        end = time_to_minutes(activity["endTime"])

        assert end > start

    assert "Charminar" in names
