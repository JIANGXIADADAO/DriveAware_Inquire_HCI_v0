import threading
from src.core.shared_state import SharedState


def test_update_and_get(shared):
    shared.update(a=1, b=2)
    a, b = shared.get("a", "b")
    assert a == 1
    assert b == 2


def test_increment_yawn_atomic(shared):
    c1 = shared.increment_yawn()
    c2 = shared.increment_yawn()
    assert c1 == 1
    assert c2 == 2
    assert shared.yawn_count == 2
    assert shared.yawn_detected is True


def test_pop_voice_intent_returns_and_clears(shared):
    shared.update(voice_intent="dynamic", voice_transcript="yes")
    v = shared.pop_voice_intent()
    assert v == "dynamic"
    assert shared.voice_intent == ""
    assert shared.voice_transcript == ""


def test_pop_voice_intent_empty(shared):
    v = shared.pop_voice_intent()
    assert v == ""


def test_concurrent_increment_yawn():
    shared = SharedState()
    N = 10
    M = 100

    def worker():
        for _ in range(M):
            shared.increment_yawn()

    threads = [threading.Thread(target=worker) for _ in range(N)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert shared.yawn_count == N * M
    assert shared.yawn_detected is True
