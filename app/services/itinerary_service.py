from app.prompts.itinerary_prompt import build_itinerary_prompt
from app.services.llm_service import LLMService
from app.validators.itinerary_validator import validate_itinerary
from app.rag.retriever import retrieve_places
from app.utils.itinerary_repair import repair_itinerary
from app.utils.weather_filter import filter_places_by_weather


llm = LLMService()


def generate_itinerary(data, weather):

    places = retrieve_places(data.destination)

    places = filter_places_by_weather(
        places,
        weather
    )

    print("\n========== FILTERED RAG PLACES ==========")
    print(f"Total places available: {len(places)}")

    print("\n========== RAG PLACE DETAILS ==========")

    for place in places:

        if isinstance(place, dict):
            print(place)

    print("\n========================================")

    public_gardens_found = False

    for place in places:

        if not isinstance(place, dict):
            continue

        place_name = str(
            place.get("place", "")
        ).strip().lower()

        if place_name == "public gardens":

            public_gardens_found = True

            print("\nPUBLIC GARDENS RAG DATA:")
            print(place)

            break

    if not public_gardens_found:

        print(
            "\nPUBLIC GARDENS IS NOT FOUND "
            "IN FILTERED RAG PLACES."
        )

    print("\n==========================================\n")

    prompt = build_itinerary_prompt(
        data,
        places,
        weather
    )

    response = llm.generate_json(
        prompt
    )

    print("\n========== LLM ITINERARY RESPONSE ==========")
    print(response)
    print("\n=============================================\n")

    itinerary = response.get(
        "itinerary",
        []
    )

    if not isinstance(itinerary, list):

        raise ValueError(
            "LLM response contains an invalid "
            "'itinerary'. Expected a list."
        )

    print("\n========== LLM ITINERARY ==========")
    print(itinerary)
    print("===================================\n")

    if (
        len(itinerary) > 0
        and isinstance(
            itinerary[0],
            dict
        )
        and isinstance(
            itinerary[0].get("activities"),
            list
        )
        and len(
            itinerary[0]["activities"]
        ) > 0
    ):

        print("\nActivities Type:")

        print(type(itinerary[0]["activities"][0]))

        print("\nFirst Activity:")
        print(itinerary[0]["activities"][0])

    itinerary = repair_itinerary(
        days=data.days,
        itinerary=itinerary,
        places=places,
        weather=weather
    )

    print("\n========== AFTER REPAIR ==========")

    print(itinerary)

    print("==================================\n")

    validate_itinerary(
        data.days,
        itinerary
    )

    print(
        "\n========== ITINERARY VALIDATION =========="
    )

    print("VALIDATION PASSED")

    print(
        "===========================================\n"
    )

    return itinerary