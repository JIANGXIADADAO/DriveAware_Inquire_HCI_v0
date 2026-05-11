import whisper
import numpy as np
import config


class STTEngine:
    def __init__(self):
        self.model = None
        self.ready = False

    def load(self):
        try:
            print(f"[STT] Loading Whisper '{config.WHISPER_MODEL_SIZE}' model...")
            self.model = whisper.load_model(config.WHISPER_MODEL_SIZE)
            self.ready = True
            print("[STT] Whisper model loaded.")
        except Exception as e:
            print(f"[STT] Failed to load Whisper model: {e}")
            self.ready = False

    def transcribe(self, audio_array, boost=3.0):
        if not self.ready or self.model is None:
            return ""
        # Boost quiet audio
        audio_float = audio_array.astype("float32") / 32768.0
        audio_float = np.clip(audio_float * boost, -1.0, 1.0)
        result = self.model.transcribe(audio_float, language="en", fp16=False)
        transcript = result["text"].strip()
        print(f"[STT] Transcript: \"{transcript}\"")
        return transcript
