import threading
import time
import cv2
import config
from src.perception.face_mesh import FaceMeshDetector
from src.perception.mar import calculate
from src.perception.yawn_detector import YawnDetector

cv2.setUseOptimized(True)


def _scale_width(frame, target_width):
    h, w = frame.shape[:2]
    if w <= target_width:
        return frame
    ratio = target_width / w
    return cv2.resize(frame, (target_width, int(h * ratio)))


class CameraThread(threading.Thread):
    def __init__(self, shared_state):
        super().__init__(daemon=True)
        self.shared = shared_state
        self.cap = cv2.VideoCapture(config.CAMERA_ID)
        if not self.cap.isOpened():
            raise RuntimeError(
                f"Cannot open camera {config.CAMERA_ID}. "
                "Is another app using it? Check your system camera "
                "permissions and close any other apps using the camera."
            )
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, config.CAMERA_FPS)
        time.sleep(config.CAMERA_WARMUP_SECONDS)
        self.detector = FaceMeshDetector()
        self.yawn_detector = YawnDetector()
        self.running = False

    def run(self):
        self.running = True
        self.shared.update(camera_alive=True)
        interval = 1.0 / config.CAMERA_FPS
        fail_count = 0
        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    fail_count += 1
                    if fail_count == 1:
                        print("[Camera] WARNING: Camera read failed. Is another app "
                              "using it?", file=__import__('sys').stderr)
                    if fail_count >= 30:
                        raise RuntimeError(
                            f"Camera failed after {fail_count} consecutive read failures"
                        )
                    time.sleep(interval)
                    continue
                fail_count = 0

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Downscale for detection; keep full-res for preview
                small = _scale_width(frame, config.DETECTION_SCALE_WIDTH)
                landmarks = self.detector.detect(small)

                if landmarks is not None:
                    mar = calculate(landmarks)
                    yawned = self.yawn_detector.update(mar)
                    self.shared.update(
                        debug_mar=mar,
                        face_detected=True,
                        camera_frame=frame,
                    )
                    if yawned:
                        self.shared.increment_yawn()
                        self.shared.update(yawn_timestamp=time.time())
                else:
                    self.shared.update(
                        debug_mar=0.0,
                        face_detected=False,
                        camera_frame=frame,
                    )
                time.sleep(interval)
        except Exception as e:
            print(f"[Camera] CRASH: {e}", file=__import__('sys').stderr)
            import traceback
            traceback.print_exc()
        finally:
            self.shared.update(camera_alive=False)
            self.running = False
            self.detector.release()
            self.cap.release()

    def stop(self):
        self.running = False
        self.join(timeout=2.0)
        self.detector.release()
        self.cap.release()
