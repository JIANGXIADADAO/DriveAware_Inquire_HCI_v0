import pytest
from collections import namedtuple
from src.core.shared_state import SharedState


@pytest.fixture
def shared():
    return SharedState()


@pytest.fixture
def sample_landmarks():
    Landmark = namedtuple("Landmark", ["x", "y", "z"])
    lm = [Landmark(0.0, 0.0, 0.0) for _ in range(478)]
    lm[61] = Landmark(0.3, 0.5, 0.0)
    lm[0] = Landmark(0.5, 0.3, 0.0)
    lm[269] = Landmark(0.7, 0.4, 0.0)
    lm[181] = Landmark(0.4, 0.4, 0.0)
    lm[291] = Landmark(0.7, 0.5, 0.0)
    lm[405] = Landmark(0.7, 0.6, 0.0)
    lm[409] = Landmark(0.4, 0.6, 0.0)
    lm[17] = Landmark(0.5, 0.7, 0.0)
    return lm


@pytest.fixture
def closed_mouth_landmarks():
    Landmark = namedtuple("Landmark", ["x", "y", "z"])
    lm = [Landmark(0.0, 0.0, 0.0) for _ in range(478)]
    lm[61] = Landmark(0.3, 0.5, 0.0)
    lm[0] = Landmark(0.5, 0.48, 0.0)
    lm[269] = Landmark(0.7, 0.49, 0.0)
    lm[181] = Landmark(0.4, 0.49, 0.0)
    lm[291] = Landmark(0.7, 0.5, 0.0)
    lm[405] = Landmark(0.7, 0.51, 0.0)
    lm[409] = Landmark(0.4, 0.51, 0.0)
    lm[17] = Landmark(0.5, 0.52, 0.0)
    return lm


@pytest.fixture
def open_mouth_landmarks():
    Landmark = namedtuple("Landmark", ["x", "y", "z"])
    lm = [Landmark(0.0, 0.0, 0.0) for _ in range(478)]
    lm[61] = Landmark(0.3, 0.5, 0.0)
    lm[0] = Landmark(0.5, 0.25, 0.0)
    lm[269] = Landmark(0.7, 0.3, 0.0)
    lm[181] = Landmark(0.4, 0.3, 0.0)
    lm[291] = Landmark(0.7, 0.5, 0.0)
    lm[405] = Landmark(0.7, 0.7, 0.0)
    lm[409] = Landmark(0.4, 0.7, 0.0)
    lm[17] = Landmark(0.5, 0.75, 0.0)
    return lm
