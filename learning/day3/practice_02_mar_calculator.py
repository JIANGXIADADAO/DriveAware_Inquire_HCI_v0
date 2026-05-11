"""
Day 3 - Practice 2: MAR calculator with exponential-decay scoring.

Goal: combine MAR calculation with a yawn detector that tolerates
brief landmark drops. This is the exact algorithm from the real
project's YawnDetector class.
"""

import time
import random


# ------------------------------------------------------------------
# 1. The yawn detector (same logic as src/perception/yawn_detector.py)
# ------------------------------------------------------------------
class YawnDetector:
    """
    Score grows when MAR > threshold, decays when it drops.
    A brief flicker only loses ~15% of evidence, not all of it.

    Tuned for ~15 fps: 30 frames (~2 seconds) of wide mouth
    reaches score ≈ 0.9, above the 0.6 trigger.
    """

    def __init__(self, threshold: float = 0.55, cooldown: float = 3.0):
        self.threshold = threshold
        self.cooldown = cooldown
        self._score = 0.0
        self._last_yawn_time = 0.0
        self._growth = 1.0 / 30 * 1.2   # 30 frames to reach 1.0
        self._decay = 0.85              # Loses 15% per frame

    def update(self, mar: float) -> bool:
        now = time.time()

        # Cooldown: no detection for N seconds after a yawn
        if now - self._last_yawn_time < self.cooldown:
            self._score = 0.0
            return False

        if mar > self.threshold:
            self._score += self._growth
            if self._score > 1.5:
                self._score = 1.5  # Cap to prevent runaway
        else:
            self._score *= self._decay

        if self._score >= 1.0:
            self._score = 0.0
            self._last_yawn_time = time.time()
            return True

        return False


# ------------------------------------------------------------------
# 2. Simulate a stream of MAR values (like camera frames)
# ------------------------------------------------------------------
def simulate_mar_stream():
    """Generate fake MAR values simulating: rest -> yawn -> rest."""
    # Resting: MAR around 0.2
    for _ in range(10):
        yield 0.2 + random.uniform(-0.05, 0.05)

    # Yawning: MAR rises to 0.6-0.7, holds for ~2 seconds
    for _ in range(30):
        yield 0.6 + random.uniform(-0.05, 0.1)

    # Back to rest
    for _ in range(20):
        yield 0.2 + random.uniform(-0.03, 0.03)

    # Another yawn (shorter, should be caught in cooldown)
    for _ in range(10):
        yield 0.55 + random.uniform(-0.02, 0.05)

    # Rest
    for _ in range(20):
        yield 0.2 + random.uniform(-0.04, 0.04)


# ------------------------------------------------------------------
# 3. Run the simulation
# ------------------------------------------------------------------
if __name__ == "__main__":
    detector = YawnDetector(threshold=0.5, cooldown=3.0)
    yawn_count = 0

    print("Simulating MAR stream at ~15 fps...")
    print(f"{'Frame':<8} {'MAR':<8} {'Score':<8} {'Event'}")
    print("-" * 45)

    for i, mar in enumerate(simulate_mar_stream()):
        yawned = detector.update(mar)
        score = detector._score

        event = ""
        if yawned:
            yawn_count += 1
            event = f"<< YAWN #{yawn_count} DETECTED >>"

        if i % 3 == 0:  # Print every 3rd frame to keep output readable
            print(f"{i:<8} {mar:<8.3f} {score:<8.3f} {event}")

        time.sleep(0.02)  # ~50 fps simulation speed

    print(f"\nTotal yawns detected: {yawn_count}")
    print("(Expected: 1 -- the second short yawn should be in cooldown)")
