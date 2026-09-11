import pytest

from app.validators.itinerary_validator import validate_itinerary

# VALID TEST ITINERARY

def make_valid_itinerary():
    return[
        {
            "day": 1,
            "title": "Hyderabad Day 1",
            "activities": [
                {
                    "name": "Charminar",
                    "startTime": "10:00 AM",
                    "endTime": "11:00 AM",
                    "bestTime": "Morning",
                    "visitDuration": "1 hour",
                    "entryFee": "₹25",
                },
                {
                    "name": "Golconda Fort",
                    "startTime": "11:30 AM",
                    "endTime": "01:30 PM",
                    "bestTime": "Evening",
                    "visitDuration": "2 hour",
                    "entryFee": "₹25",
                },
                {
                    "name": "Hussain Sagar",
                    "startTime": "02:00 PM",
                    "endTime": "04:00 PM",
                    "bestTime": "Sunset",
                    "visitDuration": "2 hour",
                    "entryFee": "Free",
                },
            ],
        },
        {
            "day": 2,
            "title": "Hyderabad Day 2",
            "activities": [
                {
                    "name": "Buddha Statue",
                    "startTime": "09:00 AM",
                    "endTime": "10:30 AM",
                    "bestTime": "Sunset",
                    "visitDuration": "1.5 hour",
                    "entryFee": "₹70",
                },
                {
                    "name": "Shilparamam",
                    "startTime": "11:00 AM",
                    "endTime": "1:00 PM",
                    "bestTime": "Evening",
                    "visitDuration": "2 hour",
                    "entryFee": "₹60",
                },
                {
                    "name": "Sudha Cars Museum",
                    "startTime": "1:30 PM",
                    "endTime": "3:00 PM",
                    "bestTime": "Afternoon",
                    "visitDuration": "1.5 hour",
                    "entryFee": "₹150",
                },
            ]
        }
    ]

# VALID ITINERARY

def test_valid_itinerary_passes():

    itinerary = make_valid_itinerary()

    result = validate_itinerary(
        days=2,
        itinerary=itinerary
    )

    assert result == result

# WRONG NUMBER OF DAYS

def test_wrong_number_of_days_fails():

     itinerary = make_valid_itinerary()

     with pytest.raises(ValueError, match="Expected 3 itinerary days"):
         validate_itinerary(
             days=3,
             itinerary=itinerary
         )

# WRONG DAY NUMBERING

def test_invalid_day_numbering_fails():

    itinerary = make_valid_itinerary()

    itinerary[0]["day"] = 2

    with pytest.raises(ValueError, match="Invalid day numbering"):
        validate_itinerary(
            days=2,
            itinerary=itinerary,
        )

# EXACTLY 3 ACTIVITIES 

def test_wrong_activity_count_fails():

    itinerary = make_valid_itinerary()

    itinerary[0]["activities"].pop()

    with pytest.raises(ValueError, match="should have exactl 3 activities"):
        validate_itinerary(
            days=2,
            itinerary=itinerary,
        )

# INVALID ACTIVITIES TYPES

def test_activities_must_be_list():

    itinerary = make_valid_itinerary()

    itinerary[0]["activities"] = "not a list"

    with pytest.raises(ValueError, match="activities must be list"):
        validate_itinerary(
            days=2,
            itinerary=itinerary,
        ) 

# MISSING REQURIED FIELD

def test_missing_requried_field_fails():

    itinerary = make_valid_itinerary()

    del itinerary[0]["activities"][0]["entryFee"]

    with pytest.raises(ValueError, match="missingrequried field 'entryFee'"):
        validate_itinerary(
            days=2,
            itinerary=itinerary,
        )

# INVALID ACTIVITY NAME

def test_invalid_activity_name_fails():

    itinerary = make_valid_itinerary()

    itinerary[0]["activities"][0]["name"] = ""

    with pytest.raises(ValueError, match="has invalid name"):
        validate_itinerary(
            days=2,
            itinerary=itinerary,
        )

# DUPLICATE ATTRACTION

def test_duplicate_attraction_fails():

    itinerary = make_valid_itinerary()

    itinerary[0]["activities"][1]["name"] = "Charminar"

    with pytest.raises(ValueError, match="Duplicate attraction found"):
        validate_itinerary(
            days=2,
            itinerary=itinerary,
        )

# INVALID TIME FORMAT

def test_invalid_time_format_failes():

    itinerary =  make_valid_itinerary()

    itinerary[0]["activities"][0]["startTime"] = "25:00 PM"

    with pytest.raises(ValueError, match="Invalid time format"):
        validate_itinerary(
            days=2,
            itinerary=itinerary,
        )

# END BEFORE STATR

def test_end_before_start_fails():

    itinerary = make_valid_itinerary()

    itinerary[0]["activities"][0]["startTime"] = "12:00 PM"
    itinerary[0]["activities"][0]["endTime"] = "11:00 AM"

    with pytest.raises(ValueError, match="invalid time range"):
        validate_itinerary(
            days=2,
            itinerary=itinerary,
        )

# OVERLAPPING ACTIVITIES

def test_overlapping_activities_fails():

    itinerary = make_valid_itinerary()

    itinerary[0]["activities"][1]["startTime"] = "10:30 AM"

    with pytest.raises(ValueError, match="overlaps the previous activity"):
        validate_itinerary(
            days=2,
            itinerary=itinerary,
        )

# LESS THAN 30 MINUTES BUFFER

def test_insufficient_buffer_fails():

    itinerary = make_valid_itinerary() 

    itinerary[0]["activities"][1]["startTime"] = "11:15 AM"

    with pytest.raises(ValueError, match="30-minute buffer"):
        validate_itinerary(
            days=2,
            itinerary=itinerary,
        )

def get_test_rag_places():
    return [
        {
            "place": "Charminar",
            "best_time": "Morning",
            "visit_duration": "1 hour",
            "entry_fee": "₹25",
            "timings": "9:30 AM - 5:30 PM",
        },
        {
            "place": "Golconda Fort",
            "best_time": "Evening",
            "visit_duration": "2 hour",
            "entry_fee": "₹25",
            "timings": "9:00 AM - 5:30 PM",
        },
        {
            "place": "Hussain Sagar",
            "best_time": "Sunset",
            "visit_duration": "2 hour",
            "entry_fee": "Free",
            "timings": "Open all day",
        },
        {
            "place": "Buddha Statue",
            "best_time": "Sunset",
            "visit_duration": "1.5 hour",
            "entry_fee": "₹70",
            "timings": "9:00 AM - 9:00 PM",
        },
        {
            "place": "Shilparamam",
            "best_time": "Evening",
            "visit_duration": "2 hour",
            "entry_fee": "₹60",
            "timings": "10:30 AM - 8:00 PM",
        },
        {
            "place": "Sudha Cars Museum",
            "best_time": "Afternoon",
            "visit_duration": "1.5 hour",
            "entry_fee": "₹150",
            "timings": "10:00 AM - 6:00 PM",
        },
    ]


def test_correct_rag_metadata_passes():
    itinerary = make_valid_itinerary()
    rag_places = get_test_rag_places()

    result = validate_itinerary(
        days=2,
        itinerary=itinerary,
        places=rag_places,
    )

    assert result == itinerary


def test_unknown_attraction_fails_rag_validation():
    itinerary = make_valid_itinerary()
    itinerary[0]["activities"][0]["name"] = "Unknown Attraction"

    rag_places = get_test_rag_places()

    with pytest.raises(ValueError, match="not present in RAG data"):
        validate_itinerary(
            days=2,
            itinerary=itinerary,
            places=rag_places,
        )


def test_wrong_visit_duration_fails_rag_validation():
    itinerary = make_valid_itinerary()
    itinerary[0]["activities"][0]["visitDuration"] = "2 hours"

    rag_places = get_test_rag_places()

    with pytest.raises(
        ValueError,
        match="visitDuration.*does not match RAG",
    ):
        validate_itinerary(
            days=2,
            itinerary=itinerary,
            places=rag_places,
        )


def test_wrong_entry_fee_fails_rag_validation():
    itinerary = make_valid_itinerary()
    itinerary[0]["activities"][0]["entryFee"] = "₹100"

    rag_places = get_test_rag_places()

    with pytest.raises(
        ValueError,
        match="entryFee.*does not match RAG",
    ):
        validate_itinerary(
            days=2,
            itinerary=itinerary,
            places=rag_places,
        )


def test_wrong_best_time_fails_rag_validation():
    itinerary = make_valid_itinerary()
    itinerary[0]["activities"][0]["bestTime"] = "Evening"

    rag_places = get_test_rag_places()

    with pytest.raises(
        ValueError,
        match="bestTime.*does not match RAG",
    ):
        validate_itinerary(
            days=2,
            itinerary=itinerary,
            places=rag_places,
        )

def test_activity_within_rag_opening_hours_passes():
    itinerary = make_valid_itinerary()
    rag_places = get_test_rag_places()

    result = validate_itinerary(
        days=2,
        itinerary=itinerary,
        places=rag_places,
    )

    assert result == itinerary


def test_activity_starting_before_opening_fails():
    itinerary = make_valid_itinerary()

    # Charminar opens at 9:30 AM
    itinerary[0]["activities"][0]["startTime"] = "9:00 AM"

    rag_places = get_test_rag_places()

    with pytest.raises(
        ValueError,
        match="starts before the attraction opens",
    ):
        validate_itinerary(
            days=2,
            itinerary=itinerary,
            places=rag_places,
        )


def test_activity_ending_after_closing_fails():
    itinerary = make_valid_itinerary()

    # Charminar closes at 5:30 PM
    itinerary[0]["activities"][0]["startTime"] = "5:00 PM"
    itinerary[0]["activities"][0]["endTime"] = "6:00 PM"

    rag_places = get_test_rag_places()

    with pytest.raises(
        ValueError,
        match="ends after the attraction closes",
    ):
        validate_itinerary(
            days=2,
            itinerary=itinerary,
            places=rag_places,
        )


def test_open_all_day_activity_passes():
    itinerary = make_valid_itinerary()

    # Hussain Sager is "Open all day"
    itinerary[0]["activities"][2]["startTime"] = "9:00 PM"
    itinerary[0]["activities"][2]["endTime"] = "11:00 PM"

    # We need to maintain the 30-minute buffer after the
    # previous activity, which ends at 1:20 PM.
    # The validator's scheduling rules allow the time itself.
    rag_places = get_test_rag_places()

    result = validate_itinerary(
        days=2,
        itinerary=itinerary,
        places=rag_places,
    )

    assert result == itinerary

def test_scheduled_duration_matches_rag():
    itinerary = make_valid_itinerary()
    rag_places = get_test_rag_places()

    result = validate_itinerary(
        days=2,
        itinerary=itinerary,
        places=rag_places,
    )

    assert result == itinerary


def test_scheduled_duration_shorter_than_rag_fails():
    itinerary = make_valid_itinerary()

    # Charminar RAG duration = 1 hour
    itinerary[0]["activities"][0]["startTime"] = "10:00 AM"
    itinerary[0]["activities"][0]["endTime"] = "10:30 AM"

    rag_places = get_test_rag_places()

    with pytest.raises(
        ValueError,
        match="scheduled duration.*60 minutes",
    ):
        validate_itinerary(
            days=2,
            itinerary=itinerary,
            places=rag_places,
        )


def test_scheduled_duration_longer_than_rag_fails():
    itinerary = make_valid_itinerary()

    # Charminar RAG duration = 1 hour
    itinerary[0]["activities"][0]["startTime"] = "10:00 AM"
    itinerary[0]["activities"][0]["endTime"] = "11:30 AM"

    rag_places = get_test_rag_places()

    with pytest.raises(
        ValueError,
        match="scheduled duration.*60 minutes",
    ):
        validate_itinerary(
            days=2,
            itinerary=itinerary,
            places=rag_places,
        )

def test_opening_hours_with_to_separator_passes():
    itinerary = make_valid_itinerary()

    itinerary[0]["activities"][0]["startTime"] = "10:00 AM"
    itinerary[0]["activities"][0]["endTime"] = "11:00 AM"

    rag_places = get_test_rag_places()

    for place in rag_places:
        if place["place"] == "Charminar":
            place["timings"] = "9:30 AM to 5:30 PM"

    result = validate_itinerary(
        days=2,
        itinerary=itinerary,
        places=rag_places,
    )

    assert result == itinerary


def test_opening_hours_with_em_dash_passes():
    itinerary = make_valid_itinerary()

    itinerary[0]["activities"][0]["startTime"] = "10:00 AM"
    itinerary[0]["activities"][0]["endTime"] = "11:00 AM"

    rag_places = get_test_rag_places()

    for place in rag_places:
        if place["place"] == "Charminar":
            place["timings"] = "9:30 AM — 5:30 PM"

    result = validate_itinerary(
        days=2,
        itinerary=itinerary,
        places=rag_places,
    )

    assert result == itinerary