import threading
import queue
import pyttsx3
import config


class TTSEngine(threading.Thread):
    def __init__(self, shared_state):
        super().__init__(daemon=True)
        self.shared = shared_state
        self._queue = queue.Queue()
        self.running = False
        self.dead = False

    def speak(self, text):
        if self.dead:
            return
        self._queue.put(text)

    def run(self):
        self.running = True
        try:
            self.shared.update(tts_alive=True)
            try:
                engine = pyttsx3.init()
                engine.setProperty("rate", config.TTS_RATE)
                engine.setProperty("volume", config.TTS_VOLUME)
                print("[TTS] Engine initialized OK.")
            except Exception as e:
                print(f"[TTS] Init failed: {e}")
                self.dead = True
                return

            while self.running:
                try:
                    text = self._queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                print(f"[TTS] Speaking: {text}")
                self.shared.update(tts_done=False)
                try:
                    engine.say(text)
                    engine.runAndWait()
                    print("[TTS] Done speaking.")
                except Exception as e:
                    print(f"[TTS] Speak error: {e}")
                    self.shared.update(tts_failed=True)
                self.shared.update(tts_done=True)
        except Exception as e:
            print(f"[TTS] CRASH: {e}", file=__import__('sys').stderr)
            import traceback
            traceback.print_exc()
        finally:
            self.shared.update(tts_alive=False)
            self.running = False

    def stop(self):
        self.running = False
        self.join(timeout=2.0)
