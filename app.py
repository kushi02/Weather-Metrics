import os
import time
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="DevOps Showcase API",
    description="A microservice fetching weather data, exposing metrics and health checks.",
    version="1.0.0"
)

# In-memory counter for DevOps metrics showcase
REQUEST_COUNT = 0

class WeatherResponse(BaseModel):
    city: str
    latitude: float
    longitude: float
    temperature_celsius: float
    windspeed_kph: float
    fetched_at: float

@app.get("/")
def read_root():
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    return {"status": "online", "message": "Welcome to the DevOps Showcase API. Try /weather or /metrics"}

@app.get("/weather", response_model=WeatherResponse)
def get_weather(lat: float = 40.7128, lon: float = -74.0060, city: str = "New York"):
    """
    Fetches real-time weather data from an external API.
    Demonstrates handling external dependencies, error boundaries, and data shaping.
    """
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        current = data.get("current_weather", {})
        return {
            "city": city,
            "latitude": lat,
            "longitude": lon,
            "temperature_celsius": current.get("temperature", 0.0),
            "windspeed_kph": current.get("windspeed", 0.0),
            "fetched_at": time.time()
        }
    except requests.RequestException as e:
        # Crucial for DevOps: logging and returning clean HTTP errors for monitoring tools
        raise HTTPException(status_code=502, detail=f"External API error: {str(e)}")

@app.get("/health")
def health_check():
    """
    Used by Docker, Kubernetes, or AWS ECS to check if the container is alive.
    """
    # You could add a database ping here if applicable
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/metrics")
def metrics():
    """
    A basic Prometheus-style metrics endpoint showcasing observability.
    """
    return {
        "total_requests_received": REQUEST_COUNT,
        "environment": os.getenv("ENV", "development"),
        "process_id": os.getpid()
    }