from pydantic import BaseModel 
from typing import Optional
from app.schemas.food import FoodRecommendation
from app.schemas.packing import PackingItem

class BudgetSummary(BaseModel):
    hotel: int
    food: int
    transport: int
    activities: int
    remaining: int

class DayPlan(BaseModel):
    day: int
    title: str
    activities: list[str]

class TripResponse(BaseModel):
    destination: str

    days: int

    budget: int

    travelers: int

    budget_summary: BudgetSummary

    itinerary: list[DayPlan]

    food_recommendations: list[FoodRecommendation]

    packing_list: Optional[list[PackingItem]] = None
    
    travel_tips: str