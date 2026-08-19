"""Minimal trips API used as the starting point for the existing-app eval.

The eval asks the agent to wire a Kafka producer into this app without
disturbing the existing routes. It has no Kafka code on purpose.
"""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Trips API")


class Trip(BaseModel):
    vendor_id: int
    pickup_datetime: str
    dropoff_datetime: str
    passenger_count: int
    trip_distance: float
    total_amount: float


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/trips")
async def create_trip(trip: Trip) -> dict:
    # TODO: publish the trip to Kafka
    return {"received": trip.model_dump()}
