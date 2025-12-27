import cv2
import json

IMAGE_PATH = "data/frames/seat_reference.jpg"
OUTPUT_JSON = "data/seats.json"
DISPLAY_SCALE = 0.6  # adjust if needed

seats = []
seat_id = 0
drawing = False
ix, iy = -1, -1

original = cv2.imread(IMAGE_PATH)
h, w = original.shape[:2]

display = cv2.resize(original, (int(w * DISPLAY_SCALE), int(h * DISPLAY_SCALE)))
image = display.copy()

def scale_up(x, y):
    return int(x / DISPLAY_SCALE), int(y / DISPLAY_SCALE)

def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, seat_id, image

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        image = display.copy()
        cv2.rectangle(image, (ix, iy), (x, y), (0, 255, 0), 2)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        x1, y1 = min(ix, x), min(iy, y)
        x2, y2 = max(ix, x), max(iy, y)

        ox1, oy1 = scale_up(x1, y1)
        ox2, oy2 = scale_up(x2, y2)

        seats.append({
            "seat_id": seat_id,
            "x1": ox1,
            "y1": oy1,
            "x2": ox2,
            "y2": oy2
        })

        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image, f"Seat {seat_id}", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

        seat_id += 1

cv2.namedWindow("Annotate Seats", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Annotate Seats", display.shape[1], display.shape[0])
cv2.setMouseCallback("Annotate Seats", draw_rectangle)

print("🪑 Draw bounding boxes for each seat")
print("➡️ Left-click & drag to draw")
print("➡️ Press 's' to save and exit")

while True:
    cv2.imshow("Annotate Seats", image)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("s"):
        break

cv2.destroyAllWindows()

with open(OUTPUT_JSON, "w") as f:
    json.dump(seats, f, indent=4)

print(f"✅ Saved {len(seats)} seats to {OUTPUT_JSON}")