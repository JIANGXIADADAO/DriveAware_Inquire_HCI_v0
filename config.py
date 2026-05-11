# Camera
CAMERA_ID = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 15
CAMERA_WARMUP_SECONDS = 2.0     # allow sensor to settle after open
DETECTION_SCALE_WIDTH = 450     # downscale before face detection
FACE_DETECTION_CONFIDENCE = 0.5

# MAR (Mouth Aspect Ratio)
MAR_THRESHOLD = 0.48              # mouth must open this wide
MAR_SUSTAINED_FRAMES = 20         # must stay open ~1.3 seconds (20f @ 15fps)
MAR_COOLDOWN_SECONDS = 2.0        # prevents re-trigger within same yawn

# MediaPipe
MP_MAX_NUM_FACES = 1
MP_REFINE_LANDMARKS = True

# Audio recording
AUDIO_SAMPLE_RATE = 16000
AUDIO_DURATION_SECONDS = 5.0

# Continuous voice listener (VAD = Voice Activity Detection)
VAD_CHUNK_SECONDS = 0.2        # Audio chunk size for continuous listening
VAD_SPEECH_THRESHOLD = 0.008   # RMS absolute minimum above this = speech
VAD_NOISE_MULTIPLIER = 3.0     # threshold = max(SPEECH_THRESHOLD, noise_floor * MULTIPLIER)
VAD_SPEECH_START_FRAMES = 3    # Consecutive chunks above threshold to trigger
VAD_SILENCE_END_FRAMES = 15    # Consecutive chunks below threshold to stop (3s)
VAD_COOLDOWN_SECONDS = 2.0     # Minimum silence after a command before listening again

# Local Whisper
WHISPER_MODEL_SIZE = "small"  # tiny, base, small, medium, large

# DeepSeek API
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# TTS
TTS_RATE = 180
TTS_VOLUME = 0.9
TTS_SPEECH_TIMEOUT = 30.0  # max seconds to wait for TTS to finish before forcing completion

# Pygame window
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# Mode colors
DYNAMIC_COLOR = (255, 80, 0)      # Warm orange
REST_COLOR = (80, 120, 255)       # Cool blue
BG_COLOR = (20, 20, 30)           # Dark background

# Climate
DYNAMIC_AC_TEMP = 18
REST_AC_TEMP = 26
COLOR_TRANSITION_SPEED = 8        # RGB steps per frame

# Voice prompts
PROMPT_INQUIRY = "You seem relaxed. Would you like to change to Dynamic Mode?"
PROMPT_CONFIRM_DYNAMIC = "Switching to Dynamic Mode."
PROMPT_CONFIRM_REST = "Staying in Rest Mode."
PROMPT_UNKNOWN = "Sorry, I didn't catch that. Would you like to change to Dynamic Mode?"
PROMPT_RETRY_EXHAUSTED = "I couldn't understand. Please use the keyboard to select a mode."
