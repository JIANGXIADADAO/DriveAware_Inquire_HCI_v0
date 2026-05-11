import sys
import numpy as np
import sounddevice as sd


def _find_best_mic():
    """Auto-detect the best microphone. Prefers real mics over stereo mix."""
    devices = sd.query_devices()
    candidates = []
    for i, d in enumerate(devices):
        if d["max_input_channels"] <= 0:
            continue
        name = d["name"].lower()
        score = 0
        if "microphone" in name or "mic" in name or "麦克风" in d["name"]:
            score += 3
        if "stereo mix" in name:
            score -= 10
        if "array" in name or "realtek" in name:
            score += 1
        candidates.append((score, i, d["name"]))

    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates


def list_microphones():
    """Print available input devices. Returns best device ID."""
    print("\n[Audio] Available microphones:")
    candidates = _find_best_mic()
    best_id = None
    for score, idx, name in candidates:
        marker = ""
        if score >= 3 and best_id is None:
            marker = " (SELECTED)"
            best_id = idx
        print(f"  [{idx}] {name} (score={score}){marker}")

    if not candidates:
        print("  WARNING: No input devices found!")
        return None

    if best_id is None:
        best_id = sd.default.device[0]
        if best_id is None and candidates:
            best_id = candidates[0][1]
        print(f"[Audio] No real mic found. Falling back to device [{best_id}].")
    else:
        print(f"[Audio] Auto-selected device [{best_id}].")

    return best_id


class AudioRecorder:
    def __init__(self):
        self.mic_id = list_microphones()
        if self.mic_id is None:
            print("[Audio] WARNING: No microphone available. Recording disabled.",
                  file=sys.stderr)
            self.best_sr = 44100
            self.best_ch = 2
            self.best_dev = None
            return

        dev_info = sd.query_devices(self.mic_id)
        native_rate = int(dev_info["default_samplerate"])
        native_ch = min(dev_info["max_input_channels"], 2)
        print(f"[Audio] Device caps: {native_ch}ch @ {native_rate}Hz")

        self.best_sr, self.best_ch, self.best_dev, self.best_rms = \
            self._find_best_config(native_rate, native_ch)
        if self.best_rms < 0.003:
            print("[Audio] Microphone input level is very low. "
                  "Check your system sound settings and increase mic gain/level.",
                  file=sys.stderr)

    def _find_best_config(self, native_rate, native_ch):
        configs = [
            (native_rate, native_ch, None),       # default device, native format
            (44100, 2, None),
            (48000, 2, None),
            (native_rate, native_ch, self.mic_id),  # explicit device
        ]
        best = (44100, 2, None, 0.0)
        for sr, ch, dev in configs:
            try:
                audio = sd.rec(int(1.0 * sr), samplerate=sr, channels=ch,
                               dtype="int16", device=dev)
                sd.wait()
                mono = audio.mean(axis=1) if (audio.ndim == 2 and audio.shape[1] > 1) else audio.flatten()
                rms = float(np.sqrt(np.mean(mono.astype("float64") ** 2))) / 32768.0
                label = f"{sr}/{ch}ch/{'default' if dev is None else f'dev{dev}'}"
                print(f"[Audio] Test [{label}]: RMS={rms:.4f}")
                if rms > best[3]:
                    best = (sr, ch, dev, rms)
            except Exception as e:
                print(f"[Audio] Test failed: {e}")
        print(f"[Audio] Selected config: {best[0]}Hz/{best[1]}ch RMS={best[3]:.4f}")
        return best

    def record(self, duration=None, shared=None):
        if self.mic_id is None:
            print("[Audio] No mic device. Skipping recording.")
            return None
        if duration is None:
            duration = 5.0

        # Check shutdown before blocking
        if shared and shared.shutdown_event.is_set():
            print("[Audio] Recording cancelled (shutdown).")
            return None

        try:
            audio = sd.rec(
                int(duration * self.best_sr),
                samplerate=self.best_sr,
                channels=self.best_ch,
                dtype="int16",
                device=self.best_dev,
            )
            sd.wait()

            if shared and shared.shutdown_event.is_set():
                print("[Audio] Recording discarded (shutdown).")
                return None

            if audio.ndim == 2 and audio.shape[1] > 1:
                audio = audio.mean(axis=1)
            else:
                audio = audio.flatten()

            if self.best_sr != 16000:
                ratio = 16000 / self.best_sr
                new_len = int(len(audio) * ratio)
                indices = np.linspace(0, len(audio) - 1, new_len)
                audio = np.interp(indices, np.arange(len(audio)), audio).astype(np.int16)

            rms = float(np.sqrt(np.mean(audio.astype("float64") ** 2)))
            rms_norm = min(rms / 32768.0, 1.0)

            if shared:
                shared.update(mic_level=rms_norm)

            print(f"[Audio] Recorded {len(audio)} samples, RMS={rms_norm:.4f}")
            if rms_norm < 0.005:
                print("[Audio] WARNING: Recording is very quiet — "
                      "check your system mic input level.",
                      file=sys.stderr)

            return audio
        except Exception as e:
            print(f"[Audio] Recording failed: {e}", file=sys.stderr)
            return None
