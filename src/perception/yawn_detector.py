import time
import config


class YawnDetector:
    """Detects yawns via exponential-decay scoring.

    Instead of requiring strictly consecutive wide-mouth frames (which
    breaks on a single dropped landmark), the score accumulates while
    MAR is above threshold and decays when it drops — a brief flicker
    loses only ~15% of accumulated evidence, not all of it.

    The growth/decay model is inspired by the AttentionScorer in
    e-candeloro/Driver-State-Detection.
    """

    def __init__(self):
        self._score = 0.0
        self._last_yawn_time = 0.0
        self.current_mar = 0.0

        # Tuned for ~15 fps: 30 frames ≈ 2 seconds of wide mouth
        # reaches score ≈ 0.9, well above the 0.6 trigger.
        self._growth = 1.0 / config.MAR_SUSTAINED_FRAMES * 1.2
        self._decay = 0.85

    def update(self, mar):
        self.current_mar = mar
        now = time.time()

        # Cooldown — prevent re-trigger within same yawn episode
        if now - self._last_yawn_time < config.MAR_COOLDOWN_SECONDS:
            self._score = 0.0
            return False

        if mar > config.MAR_THRESHOLD:
            self._score += self._growth
            if self._score > 1.5:       # cap to prevent runaway
                self._score = 1.5
        else:
            self._score *= self._decay   # exponential decay

        if self._score >= 1.0:
            self._score = 0.0
            self._last_yawn_time = now
            return True

        return False
