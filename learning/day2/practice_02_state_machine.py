"""
Day 2 - Practice 2: Simple state machine.

Goal: build a non-blocking FSM that transitions based on flags.
Pattern used in the real project's state_machine.py.
"""

import time
from enum import Enum, auto


# ------------------------------------------------------------------
# 1. Define states
# ------------------------------------------------------------------
class State(Enum):
    IDLE = auto()
    WAITING = auto()
    ACTIVE = auto()
    DONE = auto()


# ------------------------------------------------------------------
# 2. The FSM update function (called every tick)
# ------------------------------------------------------------------
def fsm_update(flags: dict) -> State:
    """
    Pure function: takes the current state + flags, returns next state.
    No sleeps, no blocking, no side effects.
    """
    state = flags["state"]

    if state == State.IDLE:
        # Transition: IDLE -> WAITING when triggered
        if flags.get("trigger"):
            print("[FSM] IDLE -> WAITING (trigger received)")
            flags["trigger"] = False  # Consume the flag
            return State.WAITING

    elif state == State.WAITING:
        # Transition: WAITING -> ACTIVE after a delay (simulated by flag)
        if flags.get("ready"):
            print("[FSM] WAITING -> ACTIVE (ready signal)")
            flags["ready"] = False
            return State.ACTIVE

    elif state == State.ACTIVE:
        # Transition: ACTIVE -> DONE when work completes
        if flags.get("work_done"):
            print("[FSM] ACTIVE -> DONE (work complete)")
            flags["work_done"] = False
            return State.DONE

    elif state == State.DONE:
        # Transition: DONE -> IDLE (reset)
        print("[FSM] DONE -> IDLE (reset)")
        return State.IDLE

    return state  # No change


# ------------------------------------------------------------------
# 3. Simulate the FSM running with external events
# ------------------------------------------------------------------
if __name__ == "__main__":
    flags = {"state": State.IDLE, "trigger": False, "ready": False, "work_done": False}

    tick = 0
    while tick < 15:
        prev = flags["state"]

        # --- Simulate external events at specific ticks ---
        if tick == 2:
            flags["trigger"] = True   # Someone sets trigger
        if tick == 5:
            flags["ready"] = True     # Timer fires
        if tick == 10:
            flags["work_done"] = True # Worker finishes

        # --- Run the FSM ---
        flags["state"] = fsm_update(flags)

        if flags["state"] != prev:
            pass  # Transition already printed inside fsm_update

        tick += 1
        time.sleep(0.3)  # Slow down so we can see it

    print("Simulation done.")
