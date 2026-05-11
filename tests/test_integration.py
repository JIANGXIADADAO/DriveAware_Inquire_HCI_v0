from src.core.shared_state import SystemState
from src.core.state_machine import update as fsm_update


def test_full_yawn_cycle(shared):
    """MONITORING → YAWN_DETECTED → INQUIRING → LISTENING → TRANSCRIBING
       → PARSING → CONFIRMING → SWITCHING → MONITORING"""
    shared.update(active_mode="rest")

    # Simulate 2 yawns
    shared.increment_yawn()
    shared.increment_yawn()

    # MONITORING → YAWN_DETECTED
    fsm_update(shared)
    assert shared.system_state == SystemState.YAWN_DETECTED

    # YAWN_DETECTED → INQUIRING
    fsm_update(shared)
    assert shared.system_state == SystemState.INQUIRING

    # TTS finishes → LISTENING
    shared.update(tts_done=True)
    fsm_update(shared)
    assert shared.system_state == SystemState.LISTENING

    # Voice pipeline signals recording done → TRANSCRIBING
    shared.update(last_intent="dynamic", worker_done=True)
    fsm_update(shared)
    assert shared.system_state == SystemState.TRANSCRIBING

    # Worker signals transcription+parsing done → PARSING
    shared.update(worker_done=True)
    fsm_update(shared)
    assert shared.system_state == SystemState.PARSING

    # Worker flags result ready → CONFIRMING
    shared.update(worker_done=True)
    fsm_update(shared)
    assert shared.system_state == SystemState.CONFIRMING

    # TTS confirms → SWITCHING
    shared.update(tts_done=True)
    fsm_update(shared)
    assert shared.system_state == SystemState.SWITCHING

    # SWITCHING → MONITORING
    fsm_update(shared)
    assert shared.system_state == SystemState.MONITORING


def test_full_cycle_rest_mode(shared):
    """Same cycle but user chooses rest."""
    shared.update(active_mode="rest")
    shared.increment_yawn()
    shared.increment_yawn()

    fsm_update(shared)  # MONITORING → YAWN_DETECTED
    fsm_update(shared)  # YAWN_DETECTED → INQUIRING
    shared.update(tts_done=True)
    fsm_update(shared)  # INQUIRING → LISTENING
    shared.update(last_intent="rest", worker_done=True)
    fsm_update(shared)  # LISTENING → TRANSCRIBING
    shared.update(worker_done=True)
    fsm_update(shared)  # TRANSCRIBING → PARSING
    shared.update(worker_done=True)
    fsm_update(shared)  # PARSING → CONFIRMING
    shared.update(tts_done=True)
    fsm_update(shared)  # CONFIRMING → SWITCHING
    fsm_update(shared)  # SWITCHING → MONITORING

    assert shared.system_state == SystemState.MONITORING


def test_retry_exhausted_returns_to_monitoring(shared):
    """After MAX_RETRIES unknown intents, FSM returns to MONITORING."""
    shared.update(active_mode="rest")
    shared.increment_yawn()
    shared.increment_yawn()

    fsm_update(shared)  # → YAWN_DETECTED
    fsm_update(shared)  # → INQUIRING
    shared.update(tts_done=True)
    fsm_update(shared)  # → LISTENING

    # First retry: unknown intent
    shared.update(last_intent="unknown", worker_done=True, retry_count=0)
    fsm_update(shared)
    assert shared.system_state == SystemState.INQUIRING
    assert shared.retry_count == 1

    # TTS re-inquiry
    shared.update(tts_done=True)
    fsm_update(shared)  # → LISTENING

    # Second retry: still unknown
    shared.update(last_intent="unknown", worker_done=True, retry_count=1)
    fsm_update(shared)
    assert shared.system_state == SystemState.INQUIRING
    assert shared.retry_count == 2

    # Third attempt (retry exhausted)
    shared.update(tts_done=True)
    fsm_update(shared)  # → LISTENING
    shared.update(last_intent="unknown", worker_done=True, retry_count=2)
    fsm_update(shared)
    assert shared.system_state == SystemState.MONITORING


def test_mode_gating_dynamic_mode_prevents_trigger(shared):
    """Yawns in dynamic mode should NOT trigger the state machine."""
    shared.update(active_mode="dynamic")
    shared.increment_yawn()
    shared.increment_yawn()

    fsm_update(shared)
    assert shared.system_state == SystemState.MONITORING


def test_mode_gating_rest_mode_allows_trigger(shared):
    """Yawns in rest mode SHOULD trigger the state machine."""
    shared.update(active_mode="rest")
    shared.increment_yawn()
    shared.increment_yawn()

    fsm_update(shared)
    assert shared.system_state == SystemState.YAWN_DETECTED


def test_transcribing_state_preserved(shared):
    """Verify TRANSCRIBING is observed (not skipped) — the Phase 3 fix."""
    shared.update(active_mode="rest")
    shared.increment_yawn()
    shared.increment_yawn()

    fsm_update(shared)  # → YAWN_DETECTED
    fsm_update(shared)  # → INQUIRING
    shared.update(tts_done=True)
    fsm_update(shared)  # → LISTENING

    # Simulate _voice_pipeline first update (recording complete, NO state change)
    shared.update(worker_done=True)
    fsm_update(shared)
    # FSM in LISTENING sees worker_done=True → transitions to TRANSCRIBING,
    # resets worker_done=False
    assert shared.system_state == SystemState.TRANSCRIBING
    assert shared.worker_done is False

    # Now simulate second _voice_pipeline update (transcription+parsing complete)
    shared.update(last_transcript="yes", last_intent="dynamic", worker_done=True)
    fsm_update(shared)
    # FSM's TRANSCRIBING handler sees worker_done=True → transitions to PARSING
    assert shared.system_state == SystemState.PARSING
