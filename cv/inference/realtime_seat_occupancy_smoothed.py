import cv2
import json
import time
import os
from ultralytics import YOLO

# -------- CONFIG --------
VIDEO_PATH = "data/videos/library.mp4"
SEATS_JSON = "data/seats.json"
CONF_THRESHOLD = 0.4
PROCESS_EVERY_N_SECONDS = 0.08  # Check every 1 second
SMOOTHING_FRAMES = 3        # Must see change 3 times to switch state
# ------------------------

# 1. Load seats
if not os.path.exists(SEATS_JSON):
    print(f"❌ Error: {SEATS_JSON} not found.")
    exit()

with open(SEATS_JSON, "r") as f:
    seats = json.load(f)

# 2. Initialize seat memory for smoothing
# state: CURRENT status, counter: how many times we've seen a DIFFERENT status
seat_memory = {
    seat["seat_id"]: {"state": "EMPTY", "counter": 0}
    for seat in seats
}

# 3. Load YOLO Model
model = YOLO("yolov8n.pt")

# 4. Point-in-Box Logic (Centroid Method)
def is_point_in_box(point, box_coords):
    px, py = point
    bx1, by1, bx2, by2 = box_coords
    return bx1 <= px <= bx2 and by1 <= py <= by2

cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print(f"❌ Error: Cannot open video.")
    exit()

# Setup Scaled Window
cv2.namedWindow("Stable Library Monitor", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Stable Library Monitor", 1280, 720)

last_processed_time = 0

print("🚀 Stable System Online. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    now = time.time()
    
    # Process AI logic at set intervals
    if now - last_processed_time >= PROCESS_EVERY_N_SECONDS:
        last_processed_time = now
        display_frame = frame.copy()

        # Run Person Detection
        results = model(frame, conf=CONF_THRESHOLD, classes=[0])
        
        person_anchors = []
        for r in results:
            if r.boxes is not None:
                for box in r.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # CALCULATE ANCHOR (Bottom-Center of person)
                    # This prevents detecting the seat behind the person's head
                    anchor_x = (x1 + x2) // 2
                    anchor_y = int(y2 - (y2 - y1) * 0.3) # 15 pixels up from the feet/bottom
                    person_anchors.append((anchor_x, anchor_y))
                    
                    # Visual: Person Box (Blue) and Anchor Point (Yellow)
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.circle(display_frame, (anchor_x, anchor_y), 5, (0, 255, 255), -1)

        occupied_count = 0

        # SEAT LOGIC WITH SMOOTHING
        for seat in seats:
            sid = seat["seat_id"]
            seat_box = (seat["x1"], seat["y1"], seat["x2"], seat["y2"])

            # Check if any person's anchor point is inside THIS seat
            is_now_detected = any(is_point_in_box(anchor, seat_box) for anchor in person_anchors)

            mem = seat_memory[sid]

            # If the current detection is DIFFERENT from the saved state
            if is_now_detected != (mem["state"] == "OCCUPIED"):
                mem["counter"] += 1
                # Only switch state if we see the change consistently
                if mem["counter"] >= SMOOTHING_FRAMES:
                    mem["state"] = "OCCUPIED" if is_now_detected else "EMPTY"
                    mem["counter"] = 0
            else:
                # If detection matches memory, reset the "change" counter
                mem["counter"] = 0

            # 5. Visualization
            status = mem["state"]
            color = (0, 0, 255) if status == "OCCUPIED" else (0, 255, 0)
            if status == "OCCUPIED": occupied_count += 1

            cv2.rectangle(display_frame, (seat["x1"], seat["y1"]), (seat["x2"], seat["y2"]), color, 2)
            cv2.putText(display_frame, f"ID:{sid}", (seat["x1"], seat["y1"] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Dashboard Overlay
        total = len(seats)
        cv2.rectangle(display_frame, (10, 10), (450, 70), (0, 0, 0), -1)
        cv2.putText(display_frame, f"Occupied: {occupied_count} | Free: {total - occupied_count}",
                    (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        cv2.imshow("Stable Library Monitor", display_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()