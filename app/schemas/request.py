from pydantic import BaseModel, Field

class TripRequest(BaseModel):
    destination: str
    days: int = Field(gt=0)
    budget: int = Field(gt=0)
    travelers: int = Field(gt=0)
    preferences: str