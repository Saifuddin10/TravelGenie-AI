from datetime import datetime
from types import SimpleNamespace

from app.services.itinerary_service import generate_itinerary


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
# HELPER
# ============================================================

def time_to_minutes(time_string):
    parsed = datetime.strptime(
        time_string.strip(),
        "%I:%M %p",
    )

    return parsed.hour * 60 + parsed.minute


# ============================================================
# REAL INTEGRATION TEST
# ============================================================

def test_generate_itinerary():

    itinerary = generate_itinerary(
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

        # Exactly 3 activities per day
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