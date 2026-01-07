import cv2
import json
import os
from ultralytics import YOLO

# -------- CONFIG --------
FRAME_PATH = "data/frames/frame_0000.jpg"   # test with one frame first
SEATS_JSON = "data/seats.json"
IOU_THRESHOLD = 0.3
CONF_THRESHOLD = 0.4
# ------------------------

# Load seats
with open(SEATS_JSON, "r") as f:
    seats = json.load(f)

# Load YOLO
model = YOLO("yolov8n.pt")

# Load frame
image = cv2.imread(FRAME_PATH)
orig = image.copy()

# Run person detection
results = model(image, conf=CONF_THRESHOLD, classes=[0])

person_boxes = []
for r in results:
    if r.boxes is None:
        continue
    for box in r.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        person_boxes.append((x1, y1, x2, y2))
        cv2.rectangle(orig, (x1, y1), (x2, y2), (255, 0, 0), 2)

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

    inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
    areaA = (ax2 - ax1) * (ay2 - ay1)
    areaB = (bx2 - bx1) * (by2 - by1)

    return inter_area / float(areaA + areaB - inter_area)

# Seat occupancy logic
seat_status = {}

for seat in seats:
    seat_box = (seat["x1"], seat["y1"], seat["x2"], seat["y2"])
    occupied = False

    for person_box in person_boxes:
        if iou(seat_box, person_box) > IOU_THRESHOLD:
            occupied = True
            break

    seat_status[seat["seat_id"]] = "OCCUPIED" if occupied else "EMPTY"

    color = (0, 0, 255) if occupied else (0, 255, 0)
    cv2.rectangle(orig,
                  (seat["x1"], seat["y1"]),
                  (seat["x2"], seat["y2"]),
                  color, 2)

# Display result
for sid, status in seat_status.items():
    print(f"Seat {sid}: {status}")

cv2.imshow("Seat Occupancy", orig)
cv2.waitKey(0)
cv2.destroyAllWindows()