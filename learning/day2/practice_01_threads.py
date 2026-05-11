"""
Day 2 - Practice 1: Basic threading with shared data.

Goal: understand how to share data between threads safely.
This is the pattern used in the real project's SharedState.
"""

import threading
import time
import random


# ------------------------------------------------------------------
# 1. A simple shared data container with a lock
# ------------------------------------------------------------------
class SharedData:
    """Thread-safe data bag. One lock for all fields (simple but works)."""

    def __init__(self):
        self.value = 0
        self.running = True
        self._lock = threading.Lock()

    def update(self, **kwargs):
        """Update one or more fields atomically."""
        with self._lock:
            for key, val in kwargs.items():
                setattr(self, key, val)

    def get(self, key):
        """Read one field atomically."""
        with self._lock:
            return getattr(self, key)


shared = SharedData()


# ------------------------------------------------------------------
# 2. A "sensor" thread that writes data
# ------------------------------------------------------------------
def sensor_thread():
    """Simulates a camera producing data at ~10 fps."""
    print("[Sensor] Started.")
    while shared.get("running"):
        # Pretend we read a sensor value
        reading = random.randint(0, 100)
        shared.update(value=reading)
        time.sleep(0.1)  # 10 readings per second
    print("[Sensor] Stopped.")


# ------------------------------------------------------------------
# 3. A "display" thread that reads data
# ------------------------------------------------------------------
def display_thread():
    """Simulates a UI that reads and shows the latest value."""
    print("[Display] Started.")
    last_shown = None
    while shared.get("running"):
        current = shared.get("value")
        if current != last_shown:
            bar = "#" * (current // 5)  # Simple ASCII bar chart
            print(f"[Display] Sensor value: {current:3d} {bar}")
            last_shown = current
        time.sleep(0.5)  # Update display 2 times per second
    print("[Display] Stopped.")


# ------------------------------------------------------------------
# 4. Start everything
# ------------------------------------------------------------------
if __name__ == "__main__":
    sensor = threading.Thread(target=sensor_thread, daemon=True)
    display = threading.Thread(target=display_thread, daemon=True)

    sensor.start()
    display.start()

    # Let them run for 3 seconds
    time.sleep(3.0)

    # Signal shutdown
    shared.update(running=False)

    # Wait for threads to finish
    sensor.join(timeout=1.0)
    display.join(timeout=1.0)

    print("Main: done.")
