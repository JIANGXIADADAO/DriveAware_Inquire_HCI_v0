from src.perception.mar import calculate


def test_closed_mouth_below_threshold(closed_mouth_landmarks):
    mar = calculate(closed_mouth_landmarks)
    assert mar < 0.55, f"Closed mouth MAR should be < 0.55, got {mar:.3f}"


def test_open_mouth_above_threshold(open_mouth_landmarks):
    mar = calculate(open_mouth_landmarks)
    assert mar > 0.55, f"Open mouth MAR should be > 0.55, got {mar:.3f}"


def test_sample_landmarks_measurable(sample_landmarks):
    mar = calculate(sample_landmarks)
    assert mar > 0.3, f"Sample landmarks should produce measureable MAR, got {mar:.3f}"


def test_zero_width_mouth_returns_zero():
    from collections import namedtuple
    Landmark = namedtuple("Landmark", ["x", "y", "z"])
    lm = [Landmark(0.5, 0.5, 0.0) for _ in range(478)]
    mar = calculate(lm)
    assert mar == 0.0, f"Zero-width mouth should return 0.0, got {mar}"
