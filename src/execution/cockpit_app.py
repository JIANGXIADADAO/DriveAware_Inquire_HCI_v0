import sys
import threading
import time
import pygame
import config
from src.core.modes import DYNAMIC_MODE, REST_MODE
from src.core.shared_state import SystemState
from src.core.state_machine import update as fsm_update
from src.execution.ambient_light import AmbientLight
from src.execution.sound_manager import SoundManager
from src.execution.cockpit_ui import CockpitUI


class CockpitApp:
    def __init__(self, shared_state, tts_engine, stt_engine, nlp_parser,
                 audio_recorder, camera_thread=None, voice_listener=None):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        )
        pygame.display.set_caption("Intelligent Cockpit - Multimodal HCI System")
        self.clock = pygame.time.Clock()
        self.shared = shared_state
        self.tts = tts_engine
        self.stt = stt_engine
        self.nlp = nlp_parser
        self.recorder = audio_recorder

        self.current_mode = REST_MODE
        self.shared.update(active_mode="rest")
        self.light = AmbientLight()
        self.sound = SoundManager()
        self.ui = CockpitUI(self.screen)
        self.running = False
        self.executor = None
        self._voice_pipeline_running = False
        self._last_inquiry_retry = -1
        self._last_confirm_intent = None
        self._camera_thread = camera_thread
        self._tts_thread = tts_engine
        self._listener_thread = voice_listener
        self._restart_counts = {"camera": 0, "listener": 0, "tts": 0}
        self._max_restarts = 3
        self._watchdog_frame = 0

    def switch_mode(self, mode):
        self.current_mode = mode

    def _apply_mode(self, intent):
        new_mode = DYNAMIC_MODE if intent == "dynamic" else REST_MODE
        if new_mode != self.current_mode:
            self.switch_mode(new_mode)
            self.sound.play(new_mode)
            self.shared.update(active_mode=new_mode.name)
            if new_mode.name == "rest":
                self.shared.update(yawn_count=0, yawn_detected=False)

    def _handle_fsm_actions(self):
        state = self.shared.system_state

        if state == SystemState.INQUIRING:
            retries = self.shared.retry_count
            if getattr(self, '_last_inquiry_retry', -1) == retries:
                # Check for timeout in case TTS engine crashed
                if not self.shared.tts_done:
                    tts_start = getattr(self, '_inquiry_tts_start', 0)
                    if tts_start and time.time() - tts_start > config.TTS_SPEECH_TIMEOUT:
                        print("[TTS] WARNING: TTS timeout, forcing completion.")
                        self.shared.update(tts_done=True)
                return
            self._last_inquiry_retry = retries

            if retries == 0:
                text = config.PROMPT_INQUIRY
            elif retries < 2:
                text = config.PROMPT_UNKNOWN
            else:
                text = config.PROMPT_RETRY_EXHAUSTED
            if self.tts:
                print(f"[TTS] Queuing: {text}")
                self.tts.speak(text)
                self._inquiry_tts_start = time.time()
            else:
                print("[TTS] No engine available, skipping.")
                self.shared.update(tts_done=True)

        elif state == SystemState.LISTENING:
            self._last_inquiry_retry = -1
            self._last_confirm_intent = None
            if not self._voice_pipeline_running:
                self._voice_pipeline_running = True
                self.executor = threading.Thread(
                    target=self._voice_pipeline, daemon=True
                )
                self.executor.start()

        elif state == SystemState.CONFIRMING:
            self._last_inquiry_retry = -1
            intent = self.shared.last_intent
            # Only fire once per CONFIRMING entry
            if getattr(self, '_last_confirm_intent', None) == intent:
                return
            self._last_confirm_intent = intent
            text = (
                config.PROMPT_CONFIRM_DYNAMIC
                if intent == "dynamic"
                else config.PROMPT_CONFIRM_REST
            )
            if self.tts:
                self.tts.speak(text)
            else:
                self.shared.update(tts_done=True)

    def _voice_pipeline(self):
        try:
            if self.shared.shutdown_event.is_set():
                return
            audio = self.recorder.record(shared=self.shared)
            if audio is None:
                self.shared.update(last_intent="unknown", worker_done=True)
                return
            if self.shared.shutdown_event.is_set():
                return

            # Signal recording complete — FSM in LISTENING transitions to TRANSCRIBING
            self.shared.update(worker_done=True)

            transcript = self.stt.transcribe(audio) if self.stt else ""
            intent = self.nlp.parse_intent(transcript)
            # Signal transcription+parsing complete — FSM in TRANSCRIBING → PARSING
            self.shared.update(
                last_transcript=transcript,
                last_intent=intent,
                worker_done=True,
            )
        finally:
            self._voice_pipeline_running = False

    def _watchdog(self):
        """Check thread health every second, restart crashed threads."""
        if not self.shared.camera_alive and self._camera_thread is not None:
            if self._restart_counts["camera"] < self._max_restarts:
                print("[Watchdog] Camera thread dead. Restarting...")
                try:
                    from src.perception.camera import CameraThread
                    new_cam = CameraThread(self.shared)
                    new_cam.start()
                    self._camera_thread = new_cam
                    self._restart_counts["camera"] += 1
                    print("[Watchdog] Camera restarted.")
                except Exception as e:
                    print(f"[Watchdog] Camera restart failed: {e}")
            elif self._restart_counts["camera"] == self._max_restarts:
                print("[Watchdog] Camera restart limit reached. Giving up.")
                self._restart_counts["camera"] += 1

        if not self.shared.tts_alive and self._tts_thread is not None:
            if self._restart_counts["tts"] < self._max_restarts:
                print("[Watchdog] TTS thread dead. Restarting...")
                try:
                    from src.interaction.tts_engine import TTSEngine
                    new_tts = TTSEngine(self.shared)
                    new_tts.start()
                    self._tts_thread = new_tts
                    self.tts = new_tts
                    self._restart_counts["tts"] += 1
                    print("[Watchdog] TTS restarted.")
                except Exception as e:
                    print(f"[Watchdog] TTS restart failed: {e}")
            elif self._restart_counts["tts"] == self._max_restarts:
                print("[Watchdog] TTS restart limit reached. Giving up.")
                self._restart_counts["tts"] += 1

        if not self.shared.listener_alive and self._listener_thread is not None:
            if self._restart_counts["listener"] < self._max_restarts:
                print("[Watchdog] VoiceListener dead. Restarting...")
                try:
                    from src.interaction.voice_listener import VoiceListener
                    new_listener = VoiceListener(
                        self.shared, self.stt, self.nlp,
                        best_sr=self.recorder.best_sr if self.recorder else 16000,
                        best_ch=self.recorder.best_ch if self.recorder else 1,
                        best_dev=self.recorder.best_dev,
                    )
                    new_listener.start()
                    self._listener_thread = new_listener
                    self._restart_counts["listener"] += 1
                    print("[Watchdog] VoiceListener restarted.")
                except Exception as e:
                    print(f"[Watchdog] VoiceListener restart failed: {e}")
            elif self._restart_counts["listener"] == self._max_restarts:
                print("[Watchdog] VoiceListener restart limit reached. Giving up.")
                self._restart_counts["listener"] += 1

    def run(self):
        self.running = True
        self.light.snap_to(self.current_mode.ambient_color)
        self.sound.play(self.current_mode)

        prev_state = self.shared.system_state
        while self.running:
            dt = self.clock.tick(config.FPS) / 1000.0

            self._watchdog_frame += 1
            if self._watchdog_frame % 60 == 0:
                self._watchdog()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    # Debug: log keycodes for all non-modifier keys
                    if event.key not in (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_LCTRL,
                                          pygame.K_RCTRL, pygame.K_LALT, pygame.K_RALT):
                        pass  # uncomment below if needed:
                        # print(f"[DEBUG] key={event.key} K_y={pygame.K_y} K_z={pygame.K_z}")
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_1:
                        self.switch_mode(DYNAMIC_MODE)
                        self.sound.play(DYNAMIC_MODE)
                        self.shared.update(active_mode="dynamic")
                    elif event.key == pygame.K_2:
                        self.switch_mode(REST_MODE)
                        self.sound.play(REST_MODE)
                        self.shared.update(active_mode="rest")
                    elif event.key == pygame.K_y or event.key == pygame.K_z:
                        try:
                            self.shared.increment_yawn()
                            self.shared.update(yawn_timestamp=0.0)
                            print(f"[DEBUG] Y/Z pressed. count={self.shared.yawn_count}")
                        except Exception as e:
                            print(f"[DEBUG] ERROR in Y handler: {e}")

            fsm_update(self.shared)
            if self.shared.system_state != prev_state:
                print(f"[DEBUG] FSM: {prev_state.name} → {self.shared.system_state.name}")
                prev_state = self.shared.system_state
            self._handle_fsm_actions()

            # Handle yawn-triggered interaction result
            intent = self.shared.last_intent
            if intent in ("dynamic", "rest"):
                self._apply_mode(intent)
                self.shared.update(last_intent="")

            # Handle continuous voice command (atomic read-and-clear)
            vcmd = self.shared.pop_voice_intent()
            if vcmd in ("dynamic", "rest"):
                print(f"[VoiceCmd] Switching to {vcmd.upper()} via voice command")
                self._apply_mode(vcmd)
                # Reset FSM to MONITORING — voice command takes priority over any in-progress flow
                self.shared.update(
                    system_state=SystemState.MONITORING,
                    retry_count=0, yawn_count=0, yawn_detected=False,
                    last_intent="", worker_done=False, tts_done=False,
                )
                if self.tts:
                    t = config.PROMPT_CONFIRM_DYNAMIC if vcmd == "dynamic" else config.PROMPT_CONFIRM_REST
                    self.tts.speak(t)

            self.light.update(self.current_mode.ambient_color)
            self.screen.fill(self.light.get_color())

            state_text = self.shared.system_state.name
            if self.shared.last_transcript:
                state_text += f' | "{self.shared.last_transcript}"'
            self.ui.render(self.current_mode, self.shared, state_text)
            pygame.display.flip()

        self.sound.stop()
        pygame.quit()
        sys.exit()
