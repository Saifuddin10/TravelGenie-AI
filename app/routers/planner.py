from fastapi import APIRouter

from app.schemas.request import TripRequest
from app.schemas.response import TripResponse
from app.services.trip_service import generate_trip

router = APIRouter(
    prefix="/planner",
    tags=["Travel Planner"]
)

@router.get("/health")
def health():
    return {
        "status": "Travel Planner API is running."
    }

@router.post("/plan-trip", response_model=TripResponse)
async def plan_trip(request: TripRequest):

    trip = await generate_trip(request)

    return trip