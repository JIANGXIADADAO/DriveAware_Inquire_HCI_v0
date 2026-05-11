"""
Day 1 - Practice 2: Opening a webcam with OpenCV.

Goal: capture live video, display it, and handle basic errors.
This is the foundation of the perception layer.
"""

import cv2

# ------------------------------------------------------------------
# 1. Open the camera
# ------------------------------------------------------------------
CAMERA_ID = 0  # Usually 0 for built-in webcam

cap = cv2.VideoCapture(CAMERA_ID)

if not cap.isOpened():
    print(f"ERROR: Cannot open camera {CAMERA_ID}.")
    print("Check: is another app using it? (Settings > Privacy > Camera)")
    exit(1)

# ------------------------------------------------------------------
# 2. Set capture properties
# ------------------------------------------------------------------
WIDTH = 640
HEIGHT = 480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

print(f"Camera {CAMERA_ID} opened. Press 'q' to quit.")
print(f"Resolution: {WIDTH}x{HEIGHT}")

# ------------------------------------------------------------------
# 3. Read and display frames
# ------------------------------------------------------------------
frame_count = 0

while True:
    ret, frame = cap.read()

    if not ret:
        # Sometimes a frame read fails -- skip it and try again
        print("WARNING: Dropped frame")
        continue

    frame_count += 1

    # --- Draw frame counter on the image ---
    cv2.putText(
        frame,
        f"Frame: {frame_count}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2,
    )

    # --- Show the frame ---
    cv2.imshow("Camera Test", frame)

    # --- Quit on 'q' ---
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ------------------------------------------------------------------
# 4. Clean up
# ------------------------------------------------------------------
cap.release()
cv2.destroyAllWindows()
print(f"Done. Captured {frame_count} frames total.")
