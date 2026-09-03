import asyncio

from app.services.itinerary_service import generate_itinerary
from app.services.budget_service import generate_budget
from app.services.food_service import generate_food
from app.services.packing_service import generate_packing
from app.services.travel_tips_service import generate_travel_tips
from app.services.weather_service import get_weather


async def generate_trip(data):

    # Fetch weather first
    weather = await asyncio.to_thread(
        get_weather,
        data.destination
    )

    # Run remaining tasks in parallel
    itinerary = asyncio.to_thread(
        generate_itinerary,
        data,
        weather
    )

    budget = asyncio.to_thread(generate_budget, data)
    food = asyncio.to_thread(generate_food, data)
    packing = asyncio.to_thread(generate_packing, data)
    travel_tips = asyncio.to_thread(generate_travel_tips, data)

    (
        itinerary,
        budget,
        food,
        packing,
        travel_tips,
    ) = await asyncio.gather(
        itinerary,
        budget,
        food,
        packing,
        travel_tips,
    )

    return {
        "destination": data.destination,
        "days": data.days,
        "budget": data.budget,
        "travelers": data.travelers,
        "weather": weather,
        "budget_summary": budget,
        "itinerary": itinerary,
        "packing_list": packing,
        "food_recommendations": food,
        "travel_tips": travel_tips
    }