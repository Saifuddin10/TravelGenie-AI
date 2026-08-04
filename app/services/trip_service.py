from app.services.itinerary_service import generate_itinerary
from app.services.budget_service import generate_budget
from app.services.food_service import generate_food
from app.services.packing_service import generate_packing
from app.services.travel_tips_service import generate_travel_tips

def generate_trip(data):

    itinerary = generate_itinerary(data)

    budget = generate_budget(data)

    food = generate_food(data)

    packing = generate_packing(data)

    travel_tips = generate_travel_tips(data)

    return {
        "destination": data.destination,
        "days": data.days,
        "budget": data.budget,
        "travelers": data.travelers,
        "budget_summary": budget, 
        "itinerary": itinerary,
        "packing_list": packing, 
        "food_recommendations": food,
        "travel_tips": travel_tips
    }