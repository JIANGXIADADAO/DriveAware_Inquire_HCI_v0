"""
Day 1 - Practice 3: Basic face detection with OpenCV Haar cascades.

Goal: find faces in a webcam feed using a pre-trained cascade classifier.
This is a lightweight first step before using MediaPipe's full face mesh.
"""

import cv2

# ------------------------------------------------------------------
# 1. Load the Haar cascade (comes with OpenCV)
# ------------------------------------------------------------------
cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(cascade_path)

if face_cascade.empty():
    print("ERROR: Could not load cascade classifier.")
    exit(1)

print("Haar cascade loaded. Looking for faces...")

# ------------------------------------------------------------------
# 2. Open camera
# ------------------------------------------------------------------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("ERROR: Cannot open camera.")
    exit(1)

# ------------------------------------------------------------------
# 3. Detection loop
# ------------------------------------------------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # Convert to grayscale (Haar cascades work on grayscale)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    # - scaleFactor=1.1: shrink image by 10% each pass (faster but may miss small faces)
    # - minNeighbors=5:  higher = fewer false positives, may miss some real faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60),  # Ignore tiny detections
    )

    # Draw rectangles around detected faces
    for i, (x, y, w, h) in enumerate(faces):
        color = (0, 255, 0)  # Green box
        thickness = 2
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
        cv2.putText(
            frame,
            f"Face {i+1}",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2,
        )

    # Show count
    cv2.putText(
        frame,
        f"Faces detected: {len(faces)}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2,
    )

    cv2.imshow("Face Detection (Haar Cascade)", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print("Done.")
