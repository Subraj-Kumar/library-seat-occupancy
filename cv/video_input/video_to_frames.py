import cv2
import os

# -------- CONFIG --------
VIDEO_PATH = "data/videos/library.mp4"
OUTPUT_DIR = "data/frames"
FRAME_INTERVAL_SECONDS = 2  # extract 1 frame every 2 seconds
# ------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    raise IOError("❌ Cannot open video file")

fps = cap.get(cv2.CAP_PROP_FPS)
frame_interval = int(fps * FRAME_INTERVAL_SECONDS)

print(f"🎥 FPS: {fps}")
print(f"⏱️ Extracting 1 frame every {FRAME_INTERVAL_SECONDS} seconds")

frame_count = 0
saved_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    if frame_count % frame_interval == 0:
        frame_name = f"frame_{saved_count:04d}.jpg"
        frame_path = os.path.join(OUTPUT_DIR, frame_name)
        cv2.imwrite(frame_path, frame)
        print(f"✅ Saved {frame_name}")
        saved_count += 1

    frame_count += 1

cap.release()
print("🎯 Frame extraction completed")