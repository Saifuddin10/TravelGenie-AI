from app.utils.itinerary_repair import parse_opening_hours

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

def _activity_duration_minutes(start_time, end_time):
    """
    Calculate activity duration in minutes.

    If the end time is earlier than the start time,
    treat the activity as crossing midnight.
    """
    start = _time_to_minutes(start_time)
    end = _time_to_minutes(end_time)

    if end < start:
        end += 24 * 60

    duration = end - start

    if duration > 12 * 60:
        raise ValueError("Activity duration cannot exceed 12 hours.")

    return duration

def _duration_to_minutes(duration):
    """
    Convert a RAG visit duration such as:
        1 hour
        2 hour
        1.5 hour
        30 minutes
    into minutes.
    """
    if not isinstance(duration, str):
        raise ValueError(f"Invalid duration value: {duration}")

    duration = duration.strip().lower()

    try:
        value = float(duration.split()[0])
    except(ValueError, IndexError):
        raise ValueError(f"Invalid duration format: '{duration}'.")

    if "hour" in duration:
        return int(value * 60)

    if "minute" in duration:
        return int(value)

    raise ValueError(
        f"Unspported duration format: '{duration}'."
    )

def _validate_opening_hours(activity, rag_match):
    """
    Validate that an activity's scheduled time falls within
    the attraction's RAG opening hours.
    """

    timings = rag_match.get("timings")

    # If opening hours are not available, skip this check.
    if not isinstance(timings, str) or not timings.strip():
        return

    ranges = parse_opening_hours(timings)

    # If the timing format cannot be parsed, skip this check.
    if not ranges:
        return

    activity_start = _time_to_minutes(activity["startTime"])
    activity_end = _time_to_minutes(activity["endTime"])

    # Check whether the complete activity fits inside
    # any available opening-hours range.
    for opening_minutes, closing_minutes in ranges:
        if (
            activity_start >= opening_minutes
            and activity_end <= closing_minutes
        ):
            return

    # Preserve specific validation errors for normal
    # same-day opening-hour ranges.
    if len(ranges) == 1:
        opening_minutes, closing_minutes = ranges[0]

        if activity_start < opening_minutes:
            raise ValueError(
                f"Activity '{activity['name']}' starts before "
                f"the attraction opens. "
                f"RAG timings: {timings}."
            )

        if activity_end > closing_minutes:
            raise ValueError(
                f"Activity '{activity['name']}' ends after "
                f"the attraction closes. "
                f"RAG timings: {timings}."
            )

    raise ValueError(
        f"Activity '{activity['name']}' is outside "
        f"the attraction's opening hours. "
        f"RAG timings: {timings}."
    )

def validate_itinerary(days, itinerary, places=None):
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

            # Validate againest RAG data when provided
            if places is not None:

                rag_match = next(
                    (
                        place
                        for place in places
                        if isinstance(place, dict)
                        and str(place.get("place", "")).strip().lower()
                        == normalized_name
                    ),
                    None,
                )

                if rag_match is None:
                    raise ValueError(
                        f"Activity '{name}' is not present in RAG data."
                    )

                # Verify authoritative RAG metadata
                if activity["visitDuration"] != rag_match.get("visit_duration"):
                    raise ValueError(
                        f"Activity '{name}' has a visitDuration "
                        f"that does not match RAG."
                    )

                if activity["entryFee"] != rag_match.get("entry_fee"):
                    raise ValueError(
                        f"Activity '{name}' has an entryFee "
                        f"that does not match RAG."
                    )

                if activity["bestTime"] != rag_match.get("best_time"):
                    raise ValueError(
                        f"Activity '{name}' has a bestTime "
                        f"that does not match RAG."
                    )

                # Validate scheduled time against RAG opening hours
                _validate_opening_hours(activity, rag_match)

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

            # Validate scheduled duration against RAG duration
            if places is not None:
                expected_duration = _duration_to_minutes(
                    rag_match.get("visit_duration")
                )

                actual_duration = _activity_duration_minutes(
                    activity["startTime"],
                    activity["endTime"],
                )

                if actual_duration != expected_duration:
                    raise ValueError(
                        f"Activity '{name}' has a scheduled duration "
                        f"of {actual_duration} minutes, but RAG "
                        f"specifies {expected_duration} minutes."
                    )

            # End must be after start

            if end <= start:

                if end < start:
                    overnight_end = end + 24 * 60

                    if overnight_end - start <= 12 * 60:
                        end = overnight_end
                    else:
                        raise ValueError(
                            f"Day {index}, activity '{name}' "
                            f"has an invalid time range: "
                            f"{activity['startTime']} - "
                            f"{activity['endTime']}."
                        )
                else:
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

    return itinerary