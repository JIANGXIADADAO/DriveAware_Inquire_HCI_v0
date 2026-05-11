"""
Day 2 - Practice 3: MediaPipe face mesh and MAR calculation.

Goal: detect 478 facial landmarks and compute Mouth Aspect Ratio.
This is the core of the yawn detection in the real project.
"""

import cv2
import mediapipe as mp
import math


# ------------------------------------------------------------------
# 1. Initialize MediaPipe
# ------------------------------------------------------------------
mp_face_mesh = mp.solutions.face_mesh

# static_image_mode=False -> treats input as video (tracks across frames)
# max_num_faces=1         -> we only care about the driver
# refine_landmarks=True   -> adds iris landmarks (extra detail around eyes)
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
)

# ------------------------------------------------------------------
# 2. MAR calculation
# ------------------------------------------------------------------
def calculate_mar(landmarks, image_width: int, image_height: int) -> float:
    """
    Mouth Aspect Ratio = vertical mouth opening / horizontal mouth width.

    MediaPipe mouth landmarks (simplified):
      - 13: upper lip (top center)
      - 14: lower lip (bottom center)
      - 78: left mouth corner
      - 308: right mouth corner

    A higher MAR means the mouth is more open (yawning).
    A typical resting MAR is 0.1-0.3; a yawn reaches 0.5-0.8.
    """
    # Convert normalized coordinates (0-1) to pixel coordinates
    def point(idx):
        lm = landmarks.landmark[idx]
        return (lm.x * image_width, lm.y * image_height)

    top = point(13)
    bottom = point(14)
    left = point(78)
    right = point(308)

    # Vertical distance (top lip to bottom lip)
    vertical = math.dist(top, bottom)

    # Horizontal distance (left corner to right corner)
    horizontal = math.dist(left, right)

    if horizontal < 0.001:
        return 0.0  # Avoid division by zero

    mar = vertical / horizontal
    return mar


# ------------------------------------------------------------------
# 3. Camera loop with MAR overlay
# ------------------------------------------------------------------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("ERROR: Cannot open camera.")
    exit(1)

print("MAR Test: open your mouth wide to see values spike.")
print("Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # MediaPipe expects RGB, OpenCV gives BGR
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w, _ = frame.shape

    # Detect face mesh
    results = face_mesh.process(rgb)

    mar = 0.0
    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0]
        mar = calculate_mar(landmarks, w, h)

        # Color-code the MAR value
        if mar > 0.55:
            color = (0, 0, 255)       # Red = likely yawning
            label = "YAWNING?"
        elif mar > 0.35:
            color = (0, 255, 255)     # Yellow = mouth open
            label = "OPEN"
        else:
            color = (0, 255, 0)       # Green = resting
            label = "REST"

        cv2.putText(
            frame,
            f"MAR: {mar:.3f} ({label})",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2,
        )

    else:
        cv2.putText(
            frame, "No face detected", (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2,
        )

    cv2.imshow("MAR Calculator", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
face_mesh.close()
print("Done.")
