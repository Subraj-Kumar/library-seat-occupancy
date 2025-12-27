import cv2
import os
from ultralytics import YOLO

# -------- CONFIG --------
FRAMES_DIR = "data/frames"
OUTPUT_DIR = "data/frames_detected"
CONF_THRESHOLD = 0.4
# ------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

# Loop through frames
for img_name in sorted(os.listdir(FRAMES_DIR)):
    img_path = os.path.join(FRAMES_DIR, img_name)

    if not img_name.endswith(".jpg"):
        continue

    image = cv2.imread(img_path)
    results = model(image, conf=CONF_THRESHOLD, classes=[0])  # class 0 = person

    for result in results:
        boxes = result.boxes
        if boxes is None:
            continue

        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])

            label = f"Person {conf:.2f}"
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                image, label, (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
            )

    out_path = os.path.join(OUTPUT_DIR, img_name)
    cv2.imwrite(out_path, image)
    print(f"✅ Processed {img_name}")

print("🎯 Person detection completed")