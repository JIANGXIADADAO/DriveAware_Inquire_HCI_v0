import sys
import logging
from dotenv import load_dotenv
from src.core.shared_state import SharedState

load_dotenv()
from src.perception.camera import CameraThread
from src.interaction.tts_engine import TTSEngine
from src.interaction.stt_engine import STTEngine
from src.interaction.nlp_parser import NLPParser
from src.interaction.audio_recorder import AudioRecorder
from src.interaction.voice_listener import VoiceListener
from src.execution.cockpit_app import CockpitApp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("main")


def main():
    logger.info("Starting Multimodal Proactive HCI System...")
    shared = SharedState()

    # Start perception
    try:
        camera = CameraThread(shared)
        camera.start()
        logger.info("Camera + perception started.")
    except Exception as e:
        logger.warning(f"Camera unavailable: {e}. Yawn detection disabled.")
        camera = None

    # Start TTS
    try:
        tts = TTSEngine(shared)
        tts.start()
        logger.info("TTS engine started.")
    except Exception as e:
        logger.warning(f"TTS unavailable: {e}. Voice output disabled.")
        tts = None

    # Load Whisper STT
    stt = STTEngine()
    try:
        stt.load()
        shared.update(whisper_ready=stt.ready)
    except Exception as e:
        logger.warning(f"Whisper failed to load: {e}. STT disabled.")

    # Init NLP parser
    nlp = NLPParser()
    shared.update(deepseek_ready=nlp.client is not None)

    # Audio recorder (auto-detects best microphone)
    try:
        recorder = AudioRecorder()
    except Exception as e:
        logger.warning(f"Audio recorder failed: {e}. Audio features disabled.")
        recorder = None

    # Continuous voice listener
    try:
        listener = VoiceListener(
            shared, stt, nlp,
            best_sr=recorder.best_sr,
            best_ch=recorder.best_ch,
            best_dev=recorder.best_dev,
        )
        listener.start()
        logger.info("Voice listener started (continuous).")
    except Exception as e:
        logger.warning(f"Voice listener failed: {e}. Voice commands disabled.")
        listener = None

    # Run UI (main thread)
    app = CockpitApp(shared, tts, stt, nlp, recorder,
                     camera_thread=camera, voice_listener=listener)
    try:
        app.run()
    finally:
        shared.shutdown_event.set()
        if listener:
            listener.stop()
        if camera:
            camera.stop()
        if tts:
            tts.stop()
        logger.info("System shut down.")


if __name__ == "__main__":
    main()
