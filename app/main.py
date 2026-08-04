from fastapi import FastAPI
from app.routers import planner

app = FastAPI(
    title="TravelGenie AI",
    description="AI-Powered Travel Planner",
    version="1.0.0"
)

app.include_router(planner.router)

@app.get("/")
def home():
    return {
        "message": "Welcome to TravelGenie AI 🚀"
    }