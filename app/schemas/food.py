from pydantic import BaseModel

class FoodRecommendation(BaseModel):
    dish: str
    description: str
    best_place: str
    estimated_price: int