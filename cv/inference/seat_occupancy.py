import cv2
import json
import os
from ultralytics import YOLO

# -------- CONFIG --------
FRAME_PATH = "data/frames/frame_0000.jpg"  # Ensure this frame exists!
SEATS_JSON = "data/seats.json"
CONF_THRESHOLD = 0.3
# ------------------------

# 1. Load seats ground truth
if not os.path.exists(SEATS_JSON):
    print(f"❌ Error: {SEATS_JSON} not found. Did you run Day 3?")
    exit()

with open(SEATS_JSON, "r") as f:
    seats = json.load(f)

# 2. Load AI Model
model = YOLO("yolov8n.pt")

# 3. Load and prepare image
image = cv2.imread(FRAME_PATH)
if image is None:
    print(f"❌ Error: Could not load image at {FRAME_PATH}")
    exit()

display_img = image.copy()

# 4. Run Person Detection
results = model(image, conf=CONF_THRESHOLD, classes=[0])

person_boxes = []
for r in results:
    if r.boxes is None:
        continue
    for box in r.boxes:
        # Get coordinates for the person
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        person_boxes.append((x1, y1, x2, y2))
        
        # DRAW PERSON: Blue box
        cv2.rectangle(display_img, (x1, y1), (x2, y2), (255, 0, 0), 2)
        
        # CALCULATE SITTING POINT (Centroid Fix):
        # We use the bottom-center of the person box as the "anchor"
        p_center_x = (x1 + x2) // 2
        p_center_y = y2 - 15  # 15 pixels up from the bottom edge
        
        # DRAW ANCHOR POINT: Cyan dot
        cv2.circle(display_img, (p_center_x, p_center_y), 5, (255, 255, 0), -1)

# 5. Seat Occupancy Logic (Point-in-Box Method)
def is_point_in_box(point, box_coords):
    px, py = point
    bx1, by1, bx2, by2 = box_coords
    return bx1 <= px <= bx2 and by1 <= py <= by2

seat_status = {}
occupied_count = 0

for seat in seats:
    seat_box = (seat["x1"], seat["y1"], seat["x2"], seat["y2"])
    is_occupied = False

    for p_box in person_boxes:
        px1, py1, px2, py2 = p_box
        # Anchor point for this specific person
        anchor_point = ((px1 + px2) // 2, py2 - 15)

        if is_point_in_box(anchor_point, seat_box):
            is_occupied = True
            occupied_count += 1
            break

    seat_status[seat["seat_id"]] = "OCCUPIED" if is_occupied else "EMPTY"

    # 6. DRAW SEATS: Red if taken, Green if free
    color = (0, 0, 255) if is_occupied else (0, 255, 0)
    cv2.rectangle(display_img, (seat["x1"], seat["y1"]), (seat["x2"], seat["y2"]), color, 2)
    
    # Label each seat
    label = f"ID:{seat['seat_id']} {seat_status[seat['seat_id']]}"
    cv2.putText(display_img, label, (seat["x1"], seat["y1"] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

# 7. ADD OVERLAY DASHBOARD
total_seats = len(seats)
available_seats = total_seats - occupied_count
cv2.rectangle(display_img, (10, 10), (300, 80), (0, 0, 0), -1) # Black background
cv2.putText(display_img, f"Total: {total_seats}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
cv2.putText(display_img, f"Available: {available_seats}", (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

# 8. SCALED DISPLAY (The Fix for Large Videos)
cv2.namedWindow("Library Seat Occupancy", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Library Seat Occupancy", 1280, 720) # Resize window to fit your screen
cv2.imshow("Library Seat Occupancy", display_img)

# Terminal Log
print("\n--- LIVE REPORT ---")
print(f"Total Seats: {total_seats} | Available: {available_seats}")
for sid, status in seat_status.items():
    print(f"Seat {sid}: {status}")

print("\n✅ Success! Press any key to exit.")
cv2.waitKey(0)
cv2.destroyAllWindows()