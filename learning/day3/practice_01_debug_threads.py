"""
Day 3 - Practice 1: Catching race conditions.

Goal: see what happens when two threads write shared data without a lock,
then fix it with a lock. This is the most common bug in the real project.
"""

import threading
import time

# ------------------------------------------------------------------
# 1. BUGGY version: no lock
# ------------------------------------------------------------------

class BadCounter:
    """Two threads increment a counter. Should reach 200000. Will it?"""

    def __init__(self):
        self.count = 0

    def increment(self):
        # This is NOT atomic in Python!
        # self.count += 1 is actually:
        #   1. read self.count
        #   2. add 1
        #   3. write self.count
        # Between step 1 and 3, another thread can read the OLD value.
        current = self.count
        current = current + 1
        self.count = current


def run_bad_counter():
    counter = BadCounter()

    def worker():
        for _ in range(100000):
            counter.increment()

    t1 = threading.Thread(target=worker)
    t2 = threading.Thread(target=worker)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    expected = 200000
    lost = expected - counter.count
    print(f"[BadCounter] Expected {expected}, got {counter.count} "
          f"(lost {lost} updates)")
    # Typical output: ~150000-190000 instead of 200000


# ------------------------------------------------------------------
# 2. FIXED version: with a lock
# ------------------------------------------------------------------

class GoodCounter:
    def __init__(self):
        self.count = 0
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:
            self.count += 1


def run_good_counter():
    counter = GoodCounter()

    def worker():
        for _ in range(100000):
            counter.increment()

    t1 = threading.Thread(target=worker)
    t2 = threading.Thread(target=worker)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    print(f"[GoodCounter] Expected 200000, got {counter.count}")


# ------------------------------------------------------------------
# 3. Debugging trick: named threads + trace prints
# ------------------------------------------------------------------

def debug_demo():
    """Show which thread is doing what at runtime."""
    shared = {"value": 0, "running": True}
    lock = threading.Lock()

    def writer(name, delta):
        while shared["running"]:
            with lock:
                shared["value"] += delta
                print(f"[{name}] wrote {shared['value']}")
            time.sleep(0.5)

    print("\n--- Debug trace (watch thread names) ---")
    t_a = threading.Thread(target=writer, args=("Writer-A", 1), daemon=True)
    t_b = threading.Thread(target=writer, args=("Writer-B", -1), daemon=True)
    t_a.start()
    t_b.start()
    time.sleep(2.0)
    shared["running"] = False
    t_a.join(timeout=1)
    t_b.join(timeout=1)


if __name__ == "__main__":
    print("=== Race condition demo ===")
    run_bad_counter()
    print()
    run_good_counter()
    debug_demo()
