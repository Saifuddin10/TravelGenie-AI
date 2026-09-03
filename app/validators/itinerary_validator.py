def _time_to_minutes(time_string):
    """
    Convert a time string such as:
        8:00 AM
        12:30 PM
        5:45 PM
        12:00 AM

    into minutes from midnight.
    """

    if not isinstance(time_string, str):
        raise ValueError(f"Invalid time value: {time_string}")

    time_string = time_string.strip().upper()

    try:
        time_part, meridiem = time_string.split()

        hour, minute = map(int, time_part.split(":"))

        if hour < 1 or hour > 12:
            raise ValueError

        if minute < 0 or minute > 59:
            raise ValueError

        if meridiem not in ("AM", "PM"):
            raise ValueError

        if meridiem == "AM":
            if hour == 12:
                hour = 0

        else:
            if hour != 12:
                hour += 12

        return hour * 60 + minute

    except Exception:
        raise ValueError(
            f"Invalid time format: '{time_string}'."
            f"Expected format like '10:30 AM'."
        )

def validate_itinerary(days, itinerary):
    """
    Validate the final repaired itinerary.

    Rules:

    - Exactly the requried number of days.
    - Correct day numbering.
    - Exactly 3 activities per day.
    - Every activity has the requried fields.
    - No duplicate attractions across the trip.
    - Activities are in chronological order.
    - Activities do not overlap.
    - At least 30 minutes between activities. 
    """

    # 1. Validate number of days

    if len(itinerary) != days:
        raise ValueError(
            f"Expected {days} itinerary days "
            f"but got {len(itinerary)}"
        )

    # Track attractions used across the entire trip

    globally_used = set()

    # 2. Validate each day

    for index, day in enumerate(itinerary, start=1):

        # Validate day number

        if day.get("day") != index:
            raise ValueError(
                f"Invalid day numbering"
                f"Expected day {index}."
            )  

        # Validate activities field

        activities = day.get("activities")

        if not isinstance(activities, list):
            raise ValueError(
                f"Day {index} activities must be list."
            )

        # Exactly 3 activities

        if len(activities) != 3:
            raise ValueError(
                f"Day {index} should have exactl 3 activities."
            )

        previous_end = None

        # Validate each activity

        for activity_index, activity in enumerate(activities, start=1):

            if not isinstance(activity, dict):
                raise ValueError(
                    f"Day {index} activity {activity_index}"
                    f"must be an object."
                )

            # Requried fields

            required_fields = [
                "name",
                "startTime",
                "endTime",
                "bestTime",
                "visitDuration",
                "entryFee"
            ]

            for field in required_fields:

                if field not in activity:
                    raise ValueError(
                        f"Day {index}, activity "
                        f"{activity_index} is missing"
                        f"requried field '{field}'."
                    )

            name = activity["name"]

            if not isinstance(name, str) or not name.strip():
                raise ValueError(
                    f"Day {index}, activity"
                    f"{activity_index} has invalid name."
                )
            normalized_name = name.strip().lower()

            # Duplicate attraction vaidation

            if normalized_name in globally_used:
                raise ValueError(
                    f"Duplicate attraction found: '{name}'."
                )
            globally_used.add(normalized_name)

            # Convert time to minute

            start = _time_to_minutes(
                activity["startTime"]
            )

            end = _time_to_minutes(
                activity["endTime"]
            )

            # End must be after start

            if end <= start:
                raise ValueError(
                    f"Day {index}, activity '{name}' "
                    f"has an invalid time range: "
                    f"{activity['startTime']} - "
                    f"{activity['endTime']}."
                )

            # Chronological order

            if previous_end is not None:

                if start < previous_end:
                    raise ValueError(
                        f"Day {index}, activity '{name}' "
                        f"overlaps the previous activity."
                    )

                # 30 minutes buffer

                gap = start - previous_end

                if gap < 30: 
                    raise ValueError(
                        f"Day {index}, activity '{name}' "
                        f"does not have the requried "
                        f"30-minute buffer. "
                        f"Gap is only {gap} minutes."
                    )

            previous_end = end

    # All validation passed

    return itinerary