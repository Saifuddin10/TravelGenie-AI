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

    prompt = build_itinerary_prompt(
        data,
        places,
        weather
    )

    response = llm.generate_json(
        prompt
    )

    itinerary = response.get(
        "itinerary",
        []
    )

    if not isinstance(itinerary, list):

        raise ValueError(
            "LLM response contains an invalid "
            "'itinerary'. Exprcted a list"
        )

    itinerary = repair_itinerary(
        days=data.days,
        itinerary=itinerary,
        places=places,
        weather=weather
    )

    validate_itinerary(
        data.days,
        itinerary,
        places
    )

    return itinerary