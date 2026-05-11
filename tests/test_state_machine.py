from src.core.shared_state import SystemState
from src.core.state_machine import update as fsm_update


def test_monitoring_stays_when_no_yawn(shared):
    shared.update(active_mode="rest", yawn_detected=False, yawn_count=0)
    fsm_update(shared)
    assert shared.system_state == SystemState.MONITORING


def test_monitoring_stays_in_dynamic_mode(shared):
    shared.update(active_mode="dynamic", yawn_detected=True, yawn_count=5)
    fsm_update(shared)
    assert shared.system_state == SystemState.MONITORING


def test_monitoring_to_yawn_detected(shared):
    shared.update(active_mode="rest", yawn_detected=True, yawn_count=2)
    fsm_update(shared)
    assert shared.system_state == SystemState.YAWN_DETECTED
    assert shared.yawn_detected is False
    assert shared.yawn_count == 0


def test_yawn_detected_to_inquiring(shared):
    shared.update(system_state=SystemState.YAWN_DETECTED)
    fsm_update(shared)
    assert shared.system_state == SystemState.INQUIRING


def test_inquiring_to_listening(shared):
    shared.update(system_state=SystemState.INQUIRING, tts_done=True)
    fsm_update(shared)
    assert shared.system_state == SystemState.LISTENING
    assert shared.tts_done is False


def test_listening_to_transcribing(shared):
    shared.update(
        system_state=SystemState.LISTENING,
        worker_done=True,
        last_intent="dynamic",
    )
    fsm_update(shared)
    assert shared.system_state == SystemState.TRANSCRIBING


def test_listening_retry_on_unknown(shared):
    shared.update(
        system_state=SystemState.LISTENING,
        worker_done=True,
        last_intent="unknown",
        retry_count=0,
    )
    fsm_update(shared)
    assert shared.system_state == SystemState.INQUIRING
    assert shared.retry_count == 1


def test_listening_retry_exhausted(shared):
    shared.update(
        system_state=SystemState.LISTENING,
        worker_done=True,
        last_intent="unknown",
        retry_count=2,
    )
    fsm_update(shared)
    assert shared.system_state == SystemState.MONITORING


def test_transcribing_to_parsing(shared):
    shared.update(
        system_state=SystemState.TRANSCRIBING,
        worker_done=True,
    )
    fsm_update(shared)
    assert shared.system_state == SystemState.PARSING


def test_parsing_to_confirming_dynamic(shared):
    shared.update(
        system_state=SystemState.PARSING,
        worker_done=True,
        last_intent="dynamic",
        retry_count=0,
    )
    fsm_update(shared)
    assert shared.system_state == SystemState.CONFIRMING


def test_parsing_to_confirming_rest(shared):
    shared.update(
        system_state=SystemState.PARSING,
        worker_done=True,
        last_intent="rest",
        retry_count=0,
    )
    fsm_update(shared)
    assert shared.system_state == SystemState.CONFIRMING


def test_parsing_retry_unknown(shared):
    shared.update(
        system_state=SystemState.PARSING,
        worker_done=True,
        last_intent="unknown",
        retry_count=1,
    )
    fsm_update(shared)
    assert shared.system_state == SystemState.INQUIRING
    assert shared.retry_count == 2


def test_parsing_retry_exhausted(shared):
    shared.update(
        system_state=SystemState.PARSING,
        worker_done=True,
        last_intent="unknown",
        retry_count=2,
    )
    fsm_update(shared)
    assert shared.system_state == SystemState.MONITORING


def test_confirming_to_switching(shared):
    shared.update(system_state=SystemState.CONFIRMING, tts_done=True)
    fsm_update(shared)
    assert shared.system_state == SystemState.SWITCHING


def test_switching_to_monitoring(shared):
    shared.update(system_state=SystemState.SWITCHING, transition_started=True)
    fsm_update(shared)
    assert shared.system_state == SystemState.MONITORING
    assert shared.yawn_count == 0
