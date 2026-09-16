import re


BUFFER_MINUTES = 30


def parse_duration(duration: str):
    """Convert duration text into minutes."""
    if not duration:
        return 60

    duration = str(duration).lower().strip()

    if "full day" in duration or "full_day" in duration:
        return 480

    try:
        value = float(duration.split()[0])

        if "hour" in duration:
            return int(value * 60)

        if "minute" in duration:
            return int(value)

    except (ValueError, IndexError):
        pass

    return 60


def format_time(minutes: int):
    """Convert minutes from midnight into 12-hour time."""
    minutes = minutes % (24 * 60)

    hour = minutes // 60
    minute = minutes % 60

    suffix = "PM" if hour >= 12 else "AM"

    display_hour = hour % 12

    if display_hour == 0:
        display_hour = 12

    return f"{display_hour}:{minute:02d} {suffix}"


def _time_to_minutes(time_string):
    """Convert a 12-hour time string into minutes from midnight."""

    if not isinstance(time_string, str):
        raise ValueError(f"Invalid time value: {time_string}")

    time_string = time_string.strip().upper()

    try:
        parts = time_string.split()

        if len(parts) != 2:
            raise ValueError

        time_part, meridiem = parts

        if ":" in time_part:
            hour, minute = map(int, time_part.split(":"))
        else:
            hour = int(time_part)
            minute = 0

        if hour < 1 or hour > 12:
            raise ValueError

        if minute < 0 or minute > 59:
            raise ValueError

        if meridiem not in ("AM", "PM"):
            raise ValueError

        if meridiem == "AM":
            if hour == 12:
                hour = 0
        elif hour != 12:
            hour += 12

        return hour * 60 + minute

    except Exception:
        raise ValueError(
            f"Invalid time format: '{time_string}'. "
            f"Expected format like '10:30 AM'."
        )


def parse_opening_hours(timings: str):
    """
    Parse all usable opening-hour ranges.

    Supports:
    9:00 AM - 7:00 PM
    11:00 AM to 9:00 PM
    10 AM — 6 PM
    """

    if not timings:
        return None

    timings = str(timings).strip()

    # Open all day
    if "open all day" in timings.lower():
        return [(0, 24 * 60)]

    # Open all night
    if "open all night" in timings.lower():
        return [(19 * 60, 24 * 60)]

    pattern = re.compile(
        r"(\d{1,2}(?::\d{2})?\s*(?:AM|PM))"
        r"\s*(?:-|—|to)\s*"
        r"(\d{1,2}(?::\d{2})?\s*(?:AM|PM))",
        re.IGNORECASE,
    )

    matches = pattern.findall(timings)

    if not matches:
        return None

    ranges = []

    for opening_text, closing_text in matches:
        try:
            opening = _time_to_minutes(opening_text)
            closing = _time_to_minutes(closing_text)

            if closing <= opening:
                closing += 24 * 60

            ranges.append((opening, closing))

        except ValueError:
            continue

    return ranges or None


def get_best_time_window(best_time: str):
    """Return preferred scheduling window for Best Time."""

    if not best_time:
        return 8 * 60, 22 * 60

    best_time = str(best_time).strip().lower()

    windows = {
        "sunrise": (5 * 60 + 30, 8 * 60),
        "morning": (8 * 60, 12 * 60),
        "afternoon": (12 * 60, 17 * 60),
        "evening": (17 * 60, 21 * 60),
        "sunset": (16 * 60 + 30, 19 * 60),
        "night": (19 * 60, 22 * 60),
        "any": (8 * 60, 22 * 60),
        "anytime": (8 * 60, 22 * 60),
    }

    return windows.get(best_time, (8 * 60, 22 * 60))


def _weather_score(place, weather=None):
    """
    Score attraction based on weather suitability.

    Higher score = better weather compatibility.
    """

    if not isinstance(place, dict):
        return -100

    if not weather:
        return 0

    condition = str(weather.get("condition", "")).strip().lower()
    temperature = weather.get("temperature")

    ideal_weather = place.get("ideal_weather", [])

    if isinstance(ideal_weather, str):
        ideal_weather = [ideal_weather]

    ideal_weather = {
        str(value).strip().lower()
        for value in ideal_weather
    }

    score = 0

    # Exact/compatible weather match
    if condition in ideal_weather:
        score += 30

    if condition in {"rain", "drizzle", "thunderstorm"}:

        if "rain" in ideal_weather:
            score += 25

        if "clouds" in ideal_weather:
            score += 15

        if str(place.get("type", "")).lower() == "indoor":
            score += 30

        if str(place.get("type", "")).lower() == "outdoor":
            score -= 25

    elif condition in {"clear", "clouds"}:

        if str(place.get("type", "")).lower() == "outdoor":
            score += 20

    # Temperature handling
    try:
        temperature = float(temperature)

        if temperature > 35:
            best_time = str(place.get("best_time", "")).lower()

            if best_time in {
                "morning",
                "evening",
                "sunset",
                "night",
                "sunrise",
            }:
                score += 15

            if str(place.get("type", "")).lower() == "indoor":
                score += 15

    except (TypeError, ValueError):
        pass

    return score


def _best_time_compatibility(place):
    """
    Score whether an attraction has a useful Best Time.
    """

    if not isinstance(place, dict):
        return -100

    best_time = str(place.get("best_time", "")).strip().lower()

    scores = {
        "sunrise": 25,
        "morning": 22,
        "afternoon": 18,
        "sunset": 25,
        "evening": 22,
        "night": 20,
        "any": 10,
        "anytime": 10,
    }

    return scores.get(best_time, 5)


def _get_nearby_places(place):
    """
    Return normalized nearby-place from the attraction.
    """
    if not isinstance(place, dict):
        return set()

    nearby = place.get("nearby_places", [])

    if isinstance(nearby, str):
        if nearby.strip().lower() in {"none", "null", ""}:
            return set()

        nearby = [nearby]

    if not isinstance(nearby, list):
        return set()

    return{
        _normalize_name(value)
        for value in nearby
        if _normalize_name(value)
    }

def _nearby_score(place, selected_places):
    """
    Reward attractions that are geographically related
    to attractions already selected for the day.

    The relationship can be defined in either direction:

        candidate -> selected
        selected -> candidate
    """
    if not isinstance(place, dict):
        return 0

    candidate_name = _normalize_name(
        place.get("place")
    )

    if not candidate_name:
        return 0

    candidate_nearby = _get_nearby_places(place)

    score = 0

    for selected in selected_places:

        if not isinstance(selected, dict):
            continue

        selected_name = _normalize_name(
            selected.get("place")
            or selected.get("name")
        )

        if not selected_name:
            continue

        selected_nearby = _get_nearby_places(selected)

        if selected_name in candidate_nearby:
            score += 25

        if candidate_name in selected_nearby:
            score += 25

    return score


def _parse_day_start(best_time):
    """
    Give a natural starting region for an attraction.
    This is used only as a scheduling preference.
    """

    best_time = str(best_time or "").strip().lower()

    mapping = {
        "sunrise": 6 * 60,
        "morning": 9 * 60,
        "afternoon": 13 * 60,
        "sunset": 16 * 60 + 30,
        "evening": 17 * 60,
        "night": 19 * 60,
        "any": 10 * 60,
        "anytime": 10 * 60,
    }

    return mapping.get(best_time, 10 * 60)


def _candidate_slots(
    preferred_start,
    preferred_end,
    duration,
    existing_activities,
    opening_ranges=None,
):
    """
    Generate valid slots.

    Best Time is preferred strongly, but can be relaxed when necessary.
    """

    occupied = []

    for activity in existing_activities:

        if not isinstance(activity, dict):
            continue

        start = activity.get("_start_minutes")
        end = activity.get("_end_minutes")

        if start is not None and end is not None:
            occupied.append((start, end))

    occupied.sort()

    if not opening_ranges:
        opening_ranges = [(8 * 60, 22 * 60)]

    candidates = []

    for opening_time, closing_time in opening_ranges:

        earliest = max(opening_time, 0)
        latest = closing_time - duration

        if latest < earliest:
            continue

        for candidate in range(earliest, latest + 1, 15):

            candidate_end = candidate + duration

            if candidate < opening_time:
                continue

            if candidate_end > closing_time:
                continue

            conflict = False

            for existing_start, existing_end in occupied:

                blocked_start = existing_start - BUFFER_MINUTES
                blocked_end = existing_end + BUFFER_MINUTES

                if (
                    candidate < blocked_end
                    and candidate_end > blocked_start
                ):
                    conflict = True
                    break

            if conflict:
                continue

            # Distance from preferred Best Time window.
            if (
                candidate >= preferred_start
                and candidate_end <= preferred_end
            ):
                distance = 0

            elif candidate_end <= preferred_start:
                distance = preferred_start - candidate_end

            elif candidate >= preferred_end:
                distance = candidate - preferred_end

            else:
                distance = min(
                    abs(candidate - preferred_start),
                    abs(candidate_end - preferred_end),
                )

            candidates.append(
                (
                    distance,
                    candidate,
                    candidate_end,
                )
            )

    candidates.sort(
        key=lambda item: (
            item[0],
            item[1],
        )
    )

    return candidates


def find_next_available_time(
    preferred_start,
    preferred_end,
    duration,
    existing_activities,
    opening_ranges=None,
):
    candidates = _candidate_slots(
        preferred_start=preferred_start,
        preferred_end=preferred_end,
        duration=duration,
        existing_activities=existing_activities,
        opening_ranges=opening_ranges,
    )

    if not candidates:
        return None

    _, start, end = candidates[0]

    return start, end


def build_activity(place, existing_activities):
    """
    Build an authoritative activity from RAG data.
    """

    if not isinstance(place, dict):
        return None

    place_name = place.get("place")

    if not place_name:
        return None

    best_time = place.get("best_time", "Morning")
    visit_duration = place.get("visit_duration", "1 hour")
    entry_fee = place.get("entry_fee", "Free")
    timings = place.get("timings", "")

    duration_minutes = parse_duration(visit_duration)

    if duration_minutes <= 0:
        return None

    preferred_start, preferred_end = get_best_time_window(
        best_time
    )

    opening_ranges = parse_opening_hours(timings)

    slot = find_next_available_time(
        preferred_start=preferred_start,
        preferred_end=preferred_end,
        duration=duration_minutes,
        existing_activities=existing_activities,
        opening_ranges=opening_ranges,
    )

    if slot is None:
        print(
            f"Skipping '{place_name}' - no valid slot for "
            f"duration {visit_duration} within opening hours "
            f"({timings}) with required buffer."
        )

        return None

    start_minutes, end_minutes = slot

    return {
        "name": place_name,
        "startTime": format_time(start_minutes),
        "endTime": format_time(end_minutes),
        "bestTime": best_time,
        "visitDuration": visit_duration,
        "entryFee": entry_fee,
        "_start_minutes": start_minutes,
        "_end_minutes": end_minutes,
    }


def clean_activity(activity):
    """Remove internal scheduling fields."""

    return {
        "name": activity["name"],
        "startTime": activity["startTime"],
        "endTime": activity["endTime"],
        "bestTime": activity["bestTime"],
        "visitDuration": activity["visitDuration"],
        "entryFee": activity["entryFee"],
    }


def get_activity_name(activity):

    if isinstance(activity, dict):
        name = activity.get("name") or activity.get("activity")
    else:
        name = activity

    if not name:
        return None

    return str(name).strip()


def _normalize_name(name):
    return str(name).strip().lower() if name else ""


def _candidate_quality_score(
    place,
    existing_activities,
    selected_places,
    weather=None,
):
    """
    Calculate how useful an attraction is as a fallback.

    Higher score = better candidate.

    The score considers:
    - weather
    - Best Time
    - opening hours
    - geographic grouping
    - schedule feasibility
    """

    if not isinstance(place, dict):
        return -10000

    score = 0

    # ---------------------------------------------------------
    # 1. Weather compatibility
    # ---------------------------------------------------------

    score += _weather_score(
        place,
        weather,
    )

    # ---------------------------------------------------------
    # 2. Best Time quality
    # ---------------------------------------------------------

    score += _best_time_compatibility(place)

    # ---------------------------------------------------------
    # 3. Geographic grouping
    # ---------------------------------------------------------

    score += _nearby_score(
        place,
        selected_places,
    )

    # ---------------------------------------------------------
    # 4. Opening hours / schedule feasibility
    # ---------------------------------------------------------

    duration = parse_duration(
        place.get("visit_duration")
    )

    best_start, best_end = get_best_time_window(
        place.get("best_time")
    )

    opening_ranges = parse_opening_hours(
        place.get("timings")
    )

    slots = _candidate_slots(
        preferred_start=best_start,
        preferred_end=best_end,
        duration=duration,
        existing_activities=existing_activities,
        opening_ranges=opening_ranges,
    )

    if not slots:
        return -10000

    best_distance = slots[0][0]

    # Very strong reward for fitting directly into Best Time.
    if best_distance == 0:
        score += 40
    else:
        # Penalize attractions that have to be moved away
        # from their preferred time.
        score -= min(best_distance // 10, 30)

    # ---------------------------------------------------------
    # 5. Prefer shorter schedule disruption
    # ---------------------------------------------------------

    score -= max(0, duration - 120) // 30

    return score


def _select_best_fallback(
    remaining_places,
    existing_activities,
    weather=None,
):
    """
    Select the best fallback attraction rather than simply
    selecting the first RAG attraction.
    """

    if not remaining_places:
        return None, None

    selected_places = [
        activity
        for activity in existing_activities
        if isinstance(activity, dict)
    ]

    ranked_candidates = []

    for place in remaining_places:

        candidate_score = _candidate_quality_score(
            place=place,
            existing_activities=existing_activities,
            selected_places=selected_places,
            weather=weather,
        )

        if candidate_score <= -10000:
            continue

        candidate_activity = build_activity(
            place,
            existing_activities,
        )

        if candidate_activity is None:
            continue

        ranked_candidates.append(
            (
                candidate_score,
                candidate_activity,
                place,
            )
        )

    if not ranked_candidates:
        return None, None

    ranked_candidates.sort(
        key=lambda item: (
            -item[0],
            _normalize_name(
                item[2].get("place")
            ),
        )
    )

    _, activity, place = ranked_candidates[0]

    return place, activity


def repair_itinerary(
    days: int,
    itinerary: list,
    places: list,
    weather=None,
):
    """
    Repair and normalize the LLM itinerary.

    Responsibilities:

    1. RAG is authoritative for attraction metadata.
    2. Deterministic scheduler is authoritative for clock times.
    3. Preserve good LLM selections when they are schedulable.
    4. Replace invalid/unschedulable selections intelligently.
    5. Use weather, Best Time, opening hours and nearby-place
       relationships when selecting fallback attractions.
    6. Avoid duplicates across the entire trip.
    """

    if not isinstance(itinerary, list):
        itinerary = []

    if not isinstance(places, list):
        places = []

    if days <= 0:
        return []

    # ---------------------------------------------------------
    # Build authoritative RAG lookup
    # ---------------------------------------------------------

    place_lookup = {}

    for place in places:

        if not isinstance(place, dict):
            continue

        place_name = place.get("place")

        if not place_name:
            continue

        normalized_name = _normalize_name(
            place_name
        )

        if normalized_name:
            place_lookup[normalized_name] = place

    # ---------------------------------------------------------
    # Normalize number of days
    # ---------------------------------------------------------

    itinerary = itinerary[:days]

    while len(itinerary) < days:

        itinerary.append(
            {
                "day": len(itinerary) + 1,
                "title": f"Day {len(itinerary) + 1}",
                "activities": [],
            }
        )

    globally_used = set()

    # ---------------------------------------------------------
    # Process every day
    # ---------------------------------------------------------

    for day_index, day in enumerate(
        itinerary,
        start=1,
    ):

        if not isinstance(day, dict):

            day = {
                "day": day_index,
                "title": f"Day {day_index}",
                "activities": [],
            }

            itinerary[day_index - 1] = day

        llm_activities = day.get(
            "activities",
            [],
        )

        if not isinstance(llm_activities, list):
            llm_activities = []

        final_activities = []
        used_today = set()

        # -----------------------------------------------------
        # First pass:
        # Preserve LLM-selected attractions if possible.
        # -----------------------------------------------------

        for activity in llm_activities:

            if len(final_activities) >= 3:
                break

            name = get_activity_name(
                activity
            )

            if not name:
                continue

            normalized_name = _normalize_name(
                name
            )

            if not normalized_name:
                continue

            # Prevent duplicates.
            if (
                normalized_name in used_today
                or normalized_name in globally_used
            ):
                continue

            place = place_lookup.get(
                normalized_name
            )

            if place is None:

                print(
                    f"Skipping '{name}' - "
                    f"not found in RAG."
                )

                continue

            final_activity = build_activity(
                place,
                final_activities,
            )

            if final_activity is None:
                continue

            final_activities.append(
                final_activity
            )

            used_today.add(
                normalized_name
            )

            globally_used.add(
                normalized_name
            )

        # -----------------------------------------------------
        # Build remaining candidate pool.
        # -----------------------------------------------------

        remaining_places = []

        for place in places:

            if not isinstance(place, dict):
                continue

            place_name = place.get("place")

            if not place_name:
                continue

            normalized_name = _normalize_name(
                place_name
            )

            if not normalized_name:
                continue

            if normalized_name in globally_used:
                continue

            remaining_places.append(place)

        # -----------------------------------------------------
        # Fill missing activities using intelligent ranking.
        # -----------------------------------------------------

        while len(final_activities) < 3:

            selected_place, selected_activity = (
                _select_best_fallback(
                    remaining_places=remaining_places,
                    existing_activities=final_activities,
                    weather=weather,
                )
            )

            if selected_place is None:
                break

            final_activities.append(
                selected_activity
            )

            normalized_name = _normalize_name(
                selected_place.get("place")
            )

            used_today.add(
                normalized_name
            )

            globally_used.add(
                normalized_name
            )

            remaining_places = [
                place
                for place in remaining_places
                if _normalize_name(
                    place.get("place")
                ) != normalized_name
            ]

        # -----------------------------------------------------
        # Sort chronologically.
        # -----------------------------------------------------

        final_activities.sort(
            key=lambda activity: activity[
                "_start_minutes"
            ]
        )

        # -----------------------------------------------------
        # Final output.
        # -----------------------------------------------------

        final_activities = final_activities[:3]

        day["activities"] = [
            clean_activity(activity)
            for activity in final_activities
        ]

        day["day"] = day_index

        if not day.get("title"):
            day["title"] = f"Day {day_index}"

    return itinerary