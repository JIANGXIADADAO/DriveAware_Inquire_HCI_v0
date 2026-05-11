"""
Day 3 - Practice 3: Voice Activity Detection (VAD).

Goal: understand energy-based VAD before using it in the real project.
This is a simplified version of the VoiceListener's VAD logic.

How it works:
  1. Read audio in small chunks (0.2 seconds).
  2. Compute RMS (root mean square) energy of each chunk.
  3. Track a noise floor (ambient room noise).
  4. Effective threshold = max(absolute_min, noise_floor * multiplier).
  5. Speech starts when N consecutive chunks are above threshold.
  6. Speech ends when M consecutive chunks are below threshold.
"""

import numpy as np
import time


# ------------------------------------------------------------------
# 1. VAD state tracker
# ------------------------------------------------------------------
class VoiceActivityDetector:
    def __init__(
        self,
        speech_threshold: float = 0.008,
        noise_multiplier: float = 3.0,
        speech_start_frames: int = 3,
        silence_end_frames: int = 15,
    ):
        self.speech_threshold = speech_threshold
        self.noise_multiplier = noise_multiplier
        self.speech_start_frames = speech_start_frames
        self.silence_end_frames = silence_end_frames

        self.noise_floor = speech_threshold  # Start conservative
        self.speech_frames = 0
        self.silence_frames = 0
        self.is_speaking = False

    def effective_threshold(self) -> float:
        return max(self.speech_threshold, self.noise_floor * self.noise_multiplier)

    def update_noise_floor(self, rms: float):
        """Slow EMA of ambient noise. Only call when NOT speaking."""
        alpha = 0.02
        self.noise_floor = (1 - alpha) * self.noise_floor + alpha * rms

    def process_chunk(self, rms: float) -> str:
        """
        Returns:
          ""        = nothing happening
          "started"  = speech just started
          "speaking" = currently in speech
          "ended"    = speech just ended
        """
        threshold = self.effective_threshold()

        if self.is_speaking:
            if rms < threshold:
                self.silence_frames += 1
                if self.silence_frames >= self.silence_end_frames:
                    self.is_speaking = False
                    self.speech_frames = 0
                    self.silence_frames = 0
                    return "ended"
            else:
                self.silence_frames = 0
            return "speaking"

        else:
            # Not speaking: update noise floor
            self.update_noise_floor(rms)

            if rms > threshold:
                self.speech_frames += 1
                if self.speech_frames >= self.speech_start_frames:
                    self.is_speaking = True
                    self.silence_frames = 0
                    return "started"
            else:
                self.speech_frames = 0
            return ""


# ------------------------------------------------------------------
# 2. Simulate a conversation with synthetic RMS values
# ------------------------------------------------------------------
def main():
    vad = VoiceActivityDetector(
        speech_threshold=0.008,
        noise_multiplier=3.0,
        speech_start_frames=3,
        silence_end_frames=15,
    )

    print("VAD Simulation")
    print("-" * 50)
    print(f"{'Time':<8} {'RMS':<10} {'Threshold':<10} {'Event'}")
    print("-" * 50)

    # Build a fake audio timeline:
    chunks = (
        # Ambient noise (quiet room)
        [(0.003, "ambient")] * 10
        +
        # Someone starts speaking
        [(0.015, "speech")] * 5
        +
        # Speaking continues
        [(0.012, "speech")] * 20
        +
        # Short pause (RMS drops but not enough to end)
        [(0.005, "pause")] * 5
        +
        # Speaking resumes
        [(0.014, "speech")] * 15
        +
        # Silence (speech ends)
        [(0.002, "silence")] * 20
        +
        # Ambient again
        [(0.003, "ambient")] * 10
    )

    for i, (rms, label) in enumerate(chunks):
        # Add small random jitter
        rms_jittered = rms + np.random.normal(0, 0.0005)
        rms_jittered = max(0, rms_jittered)

        result = vad.process_chunk(rms_jittered)

        if result:
            marker = f"<< {result.upper()} >>"
        else:
            marker = ""

        if i % 5 == 0 or result:
            thr = vad.effective_threshold()
            nf = vad.noise_floor
            print(f"{i*0.2:4.1f}s    "
                  f"{rms_jittered:<10.4f} "
                  f"{thr:<10.4f} "
                  f"{marker}")

        time.sleep(0.01)

    print("-" * 50)
    print(f"Final noise floor: {vad.noise_floor:.5f}")
    print("Done.")


if __name__ == "__main__":
    main()
