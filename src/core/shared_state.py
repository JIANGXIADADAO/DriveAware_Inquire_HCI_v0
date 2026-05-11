import threading
from dataclasses import dataclass, field
from enum import Enum, auto


class SystemState(Enum):
    MONITORING = auto()
    YAWN_DETECTED = auto()
    INQUIRING = auto()
    LISTENING = auto()
    TRANSCRIBING = auto()
    PARSING = auto()
    CONFIRMING = auto()
    SWITCHING = auto()


@dataclass
class SharedState:
    # Camera → state machine
    yawn_detected: bool = False
    yawn_timestamp: float = 0.0
    yawn_count: int = 0  # number of yawns detected in current session

    # State machine → UI
    system_state: SystemState = SystemState.MONITORING
    transition_started: bool = False

    # Interaction results
    last_transcript: str = ""
    last_intent: str = ""  # "dynamic", "rest", "unknown"
    retry_count: int = 0

    # TTS status
    tts_done: bool = False
    tts_failed: bool = False
    worker_done: bool = False

    # API available flags
    whisper_ready: bool = False
    deepseek_ready: bool = False

    # Current cockpit mode (used by FSM to gate yawn detection)
    active_mode: str = "rest"     # "rest" or "dynamic"

    # Voice commands (continuous listener)
    voice_intent: str = ""        # "dynamic", "rest", or "" — set by continuous listener
    voice_transcript: str = ""    # last transcript from continuous listener

    # Thread health (for watchdog)
    camera_alive: bool = False
    tts_alive: bool = False
    listener_alive: bool = False

    # Debug / visualization
    camera_frame: object = None   # Latest RGB frame from camera (ndarray)
    debug_mar: float = 0.0
    face_detected: bool = False
    mic_level: float = 0.0        # Current microphone RMS level (0.0 - 1.0)

    shutdown_event: threading.Event = field(default_factory=threading.Event)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def update(self, **kwargs):
        with self._lock:
            for key, val in kwargs.items():
                setattr(self, key, val)

    def get(self, *keys):
        with self._lock:
            return tuple(getattr(self, k) for k in keys)

    def increment_yawn(self):
        """Atomically increment yawn_count and return new value."""
        with self._lock:
            self.yawn_count += 1
            self.yawn_detected = True
            return self.yawn_count

    def pop_voice_intent(self):
        """Atomically read and clear voice_intent."""
        with self._lock:
            v = self.voice_intent
            if v:
                self.voice_intent = ""
                self.voice_transcript = ""
            return v
