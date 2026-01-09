from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(title="Library Seat Occupancy API")

# ---------------- GLOBAL STATE ----------------
seat_state = {
    "total": 0,
    "occupied": 0,
    "empty": 0,
    "seats": {},
    "last_updated": None
}

clients = []  # active websocket connections
# ------------------------------------------------


# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# --------------------------------------


# ---------------- HELPERS ----------------
async def broadcast(data):
    dead_clients = []
    for ws in clients:
        try:
            await ws.send_json(data)
        except:
            dead_clients.append(ws)

    for ws in dead_clients:
        clients.remove(ws)
# ----------------------------------------


# ---------------- ROUTES ----------------
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
async def update_seats(payload: dict):
    seat_state["total"] = payload["total"]
    seat_state["occupied"] = payload["occupied"]
    seat_state["empty"] = payload["empty"]
    seat_state["seats"] = payload["seats"]
    seat_state["last_updated"] = datetime.now().strftime("%H:%M:%S")

    await broadcast(seat_state)
    return {"message": "Seat data updated"}
# ----------------------------------------


# ---------------- WEBSOCKET ----------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)

    try:
        while True:
            await websocket.receive_text()  # keep-alive
    except WebSocketDisconnect:
        clients.remove(websocket)
# -----------------------------------------