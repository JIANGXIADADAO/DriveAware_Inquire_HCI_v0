import time
from src.core.shared_state import SystemState


MAX_RETRIES = 2
TRANSITION_DURATION = 1.0  # seconds for SWITCHING animation


def update(shared):
    state = shared.system_state
    now = time.time()

    if state == SystemState.MONITORING:
        yawn, count = shared.get("yawn_detected", "yawn_count")
        # Only trigger proactive interaction when in Rest Mode
        if yawn and count >= 2 and shared.active_mode == "rest":
            shared.update(
                system_state=SystemState.YAWN_DETECTED,
                yawn_detected=False,
                yawn_count=0,
            )
            return

    elif state == SystemState.YAWN_DETECTED:
        # Brief gate to debounce, then proceed
        shared.update(system_state=SystemState.INQUIRING)
        return

    elif state == SystemState.INQUIRING:
        if shared.tts_done:
            shared.update(
                system_state=SystemState.LISTENING,
                tts_done=False,
            )
            return

    elif state == SystemState.LISTENING:
        if shared.worker_done:
            # Check if worker aborted early (no audio captured)
            if shared.last_intent == "unknown":
                retries = shared.retry_count
                if retries < MAX_RETRIES:
                    shared.update(
                        system_state=SystemState.INQUIRING,
                        worker_done=False,
                        retry_count=retries + 1,
                    )
                else:
                    shared.update(
                        system_state=SystemState.MONITORING,
                        worker_done=False,
                        retry_count=0,
                        yawn_count=0,
                        yawn_detected=False,
                    )
            else:
                shared.update(
                    system_state=SystemState.TRANSCRIBING,
                    worker_done=False,
                )
            return

    elif state == SystemState.TRANSCRIBING:
        if shared.worker_done:
            shared.update(
                system_state=SystemState.PARSING,
                worker_done=False,
            )
            return

    elif state == SystemState.PARSING:
        if shared.worker_done:
            intent, retries = shared.get("last_intent", "retry_count")
            shared.update(worker_done=False)
            if intent in ("dynamic", "rest"):
                shared.update(
                    system_state=SystemState.CONFIRMING,
                    retry_count=0,
                )
            elif retries < MAX_RETRIES:
                shared.update(
                    system_state=SystemState.INQUIRING,
                    retry_count=retries + 1,
                )
            else:
                shared.update(
                    system_state=SystemState.MONITORING,
                    retry_count=0,
                    yawn_count=0,
                    yawn_detected=False,
                )
            return

    elif state == SystemState.CONFIRMING:
        if shared.tts_done:
            shared.update(
                system_state=SystemState.SWITCHING,
                tts_done=False,
                transition_started=True,
            )
            return

    elif state == SystemState.SWITCHING:
        if shared.transition_started:
            shared.update(transition_started=False)
        shared.update(system_state=SystemState.MONITORING,
                       yawn_count=0, yawn_detected=False)
        return
