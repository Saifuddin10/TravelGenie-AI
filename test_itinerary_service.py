from types import SimpleNamespace

from app.services.itinerary_service import generate_itinerary


# ============================================================
# TEST INPUT
# ============================================================

data = SimpleNamespace(
    destination="Hyderabad",
    days=3,
)

weather = {
    "condition": "clear",
    "temperature": 32,
}


# ============================================================
# RUN REAL generate_itinerary()
# ============================================================

print("=" * 60)
print("RUNNING REAL ITINERARY SERVICE INTEGRATION TEST")
print("=" * 60)

try:

    itinerary = generate_itinerary(
        data=data,
        weather=weather,
    )

except Exception as e:

    print("\n❌ INTEGRATION TEST FAILED")
    print(f"Error: {e}")

    raise


# ============================================================
# PRINT FINAL RESULT
# ============================================================

print("\n" + "=" * 60)
print("FINAL GENERATED + REPAIRED ITINERARY")
print("=" * 60)

for day in itinerary:

    print(
        f"\nDay {day.get('day')} - "
        f"{day.get('title')}"
    )

    for activity in day.get("activities", []):

        print(
            f"  {activity.get('name')} | "
            f"{activity.get('startTime')} - "
            f"{activity.get('endTime')} | "
            f"Best: {activity.get('bestTime')} | "
            f"Duration: {activity.get('visitDuration')} | "
            f"Fee: {activity.get('entryFee')}"
        )


# ============================================================
# BASIC VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("INTEGRATION VALIDATION")
print("=" * 60)

errors = []

if not isinstance(itinerary, list):
    errors.append(
        "generate_itinerary() did not return a list."
    )

elif len(itinerary) != data.days:
    errors.append(
        f"Expected {data.days} days, "
        f"got {len(itinerary)}."
    )

all_names = []

for day in itinerary:

    activities = day.get(
        "activities",
        []
    )

    if len(activities) > 3:
        errors.append(
            f"Day {day.get('day')} has "
            f"more than 3 activities."
        )

    for activity in activities:

        name = activity.get("name")

        if not name:
            errors.append(
                f"Day {day.get('day')} contains "
                "an activity without a name."
            )
            continue

        all_names.append(
            name.strip().lower()
        )

        if not activity.get("startTime"):
            errors.append(
                f"{name} has no startTime."
            )

        if not activity.get("endTime"):
            errors.append(
                f"{name} has no endTime."
            )

        if not activity.get("bestTime"):
            errors.append(
                f"{name} has no bestTime."
            )

        if not activity.get("visitDuration"):
            errors.append(
                f"{name} has no visitDuration."
            )

        if not activity.get("entryFee"):
            errors.append(
                f"{name} has no entryFee."
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
        f"Duplicate attractions found: "
        f"{sorted(duplicates)}"
    )


# ============================================================
# FINAL RESULT
# ============================================================

if errors:

    print("\n❌ INTEGRATION TEST FAILED\n")

    for error in errors:
        print(f"  - {error}")

else:

    print("\n✅ INTEGRATION TEST PASSED")

    print(
        "Real generate_itinerary() successfully "
        "produced a valid repaired itinerary."
    )