from fastapi import FastAPI
from datetime import datetime
from backend.app.state import seat_state

app = FastAPI(title="Library Seat Occupancy API")

@app.get("/")
def root():
    return {"status": "Backend running"}

@app.get("/status")
def get_status():
    return seat_state

@app.get("/seats")
def get_seats():
    return seat_state["seats"]

@app.post("/update")
def update_seats(payload: dict):
    seat_state["total"] = payload["total"]
    seat_state["occupied"] = payload["occupied"]
    seat_state["empty"] = payload["empty"]
    seat_state["seats"] = payload["seats"]
    seat_state["last_updated"] = datetime.now().strftime("%H:%M:%S")

    return {"message": "Seat data updated"}