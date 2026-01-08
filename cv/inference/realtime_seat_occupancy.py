import cv2
import json
import time
import os
from ultralytics import YOLO

# -------- CONFIG --------
VIDEO_PATH = "data/videos/library.mp4"
SEATS_JSON = "data/seats.json"
CONF_THRESHOLD = 0.35
IOU_THRESHOLD = 0.25
PROCESS_EVERY_N_SECONDS = 2  # The "Inference Gap"
# ------------------------

# Load seats
if not os.path.exists(SEATS_JSON):
    print(f"❌ Error: {SEATS_JSON} not found.")
    exit()

with open(SEATS_JSON, "r") as f:
    seats = json.load(f)

# Load model
model = YOLO("yolov8n.pt")

# IoU function
def iou(boxA, boxB):
    ax1, ay1, ax2, ay2 = boxA
    bx1, by1, bx2, by2 = boxB
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    if inter_x2 <= inter_x1 or inter_y2 <= inter_y1:
        return 0.0

    inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
    areaA = (ax2 - ax1) * (ay2 - ay1)
    areaB = (bx2 - bx1) * (by2 - by1)
    return inter_area / float(areaA + areaB - inter_area)

cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print(f"❌ Error: Cannot open video at {VIDEO_PATH}")
    exit()

last_processed_time = 0

# Setup Resizable Window
cv2.namedWindow("Real-Time Seat Occupancy", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Real-Time Seat Occupancy", 1280, 720)

print("🚀 Starting Live Stream... Press 'q' to stop.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    current_time = time.time()

    # ONLY RUN AI LOGIC EVERY N SECONDS
    if current_time - last_processed_time >= PROCESS_EVERY_N_SECONDS:
        last_processed_time = current_time
        
        # Run person detection
        results = model(frame, conf=CONF_THRESHOLD, classes=[0])

        person_boxes = []
        for r in results:
            if r.boxes is not None:
                for box in r.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    person_boxes.append((x1, y1, x2, y2))
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

        occupied_count = 0

        # Seat occupancy logic
        for seat in seats:
            seat_box = (seat["x1"], seat["y1"], seat["x2"], seat["y2"])
            occupied = False

            for person_box in person_boxes:
                if iou(seat_box, person_box) > IOU_THRESHOLD:
                    occupied = True
                    break

            color = (0, 0, 255) if occupied else (0, 255, 0)
            if occupied:
                occupied_count += 1

            cv2.rectangle(frame, (seat["x1"], seat["y1"]), (seat["x2"], seat["y2"]), color, 2)

        # Update Display Text
        empty_count = len(seats) - occupied_count
        timestamp = time.strftime("%H:%M:%S")
        
        # Print to Terminal
        print(f"[{timestamp}] Occupied: {occupied_count} | Available: {empty_count}")

        # Add visual overlay
        cv2.rectangle(frame, (10, 10), (450, 60), (0, 0, 0), -1)
        cv2.putText(frame, f"LIVE: {occupied_count} Occupied | {empty_count} Free", 
                    (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        # Show the updated frame
        cv2.imshow("Real-Time Seat Occupancy", frame)

    # Maintain smooth playback (Wait 1ms between frames)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()