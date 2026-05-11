import time
from src.perception.yawn_detector import YawnDetector


def test_no_yawn_on_low_mar():
    detector = YawnDetector()
    for _ in range(60):
        result = detector.update(0.3)
    assert result is False
    assert detector._score < 0.6


def test_yawn_triggered_after_sustained_high_mar(monkeypatch):
    detector = YawnDetector()
    monkeypatch.setattr(detector, "_last_yawn_time", 0.0)

    results = []
    for _ in range(25):
        results.append(detector.update(0.65))

    assert any(results), "Should trigger a yawn within 25 frames of high MAR"


def test_cooldown_prevents_retrigger(monkeypatch):
    detector = YawnDetector()
    monkeypatch.setattr(detector, "_last_yawn_time", 0.0)

    for _ in range(35):
        detector.update(0.65)

    results = []
    for _ in range(10):
        results.append(detector.update(0.65))
    assert not any(results), "Cooldown should prevent immediate re-trigger"


def test_brief_dip_does_not_reset(monkeypatch):
    detector = YawnDetector()
    monkeypatch.setattr(detector, "_last_yawn_time", 0.0)

    # Build partial evidence without triggering (12 * 0.06 = 0.72 < 1.0)
    for _ in range(12):
        detector.update(0.65)

    # Brief mouth closure — score decays but evidence persists
    for _ in range(2):
        detector.update(0.3)

    # Recover and finish the yawn
    results = []
    for _ in range(15):
        results.append(detector.update(0.65))

    assert any(results), "Brief dip should not reset evidence"


def test_score_capped():
    detector = YawnDetector()
    detector._last_yawn_time = time.time() + 9999
    for _ in range(100):
        detector.update(0.8)
    assert detector._score <= 1.5, "Score should not exceed cap of 1.5"


def test_expired_cooldown_allows_new_yawn(monkeypatch):
    detector = YawnDetector()
    monkeypatch.setattr(detector, "_last_yawn_time", 0.0)

    for _ in range(35):
        detector.update(0.65)

    monkeypatch.setattr(detector, "_last_yawn_time", time.time() - 10.0)

    results = []
    for _ in range(35):
        results.append(detector.update(0.65))
    assert any(results), "Should trigger again after cooldown expires"
