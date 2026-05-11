# Proactive In-Cabin Interaction — Driver State Awareness Research Prototype

> An HCI research prototype exploring **inquiry-based interaction** in intelligent cockpits: the system observes, suggests, and asks — the driver decides. No alarms, no forced actions.

## What This Is

A research prototype for proactive interaction and shared control in intelligent vehicle cockpits. The system detects driver yawns via facial landmark analysis (MediaPipe + MAR), then proactively initiates a voice inquiry. The driver responds by voice (Whisper STT + NLP), choosing whether to switch to **Dynamic Mode** or stay in **Rest Mode**. The cockpit environment (ambient light, sound, virtual climate) adapts accordingly.

Core proposition: **the system handles perception and suggestion; decision authority stays with the human.**

## Features

- Real-time facial landmark MAR calculation with exponential-decay yawn scoring
- Accumulates 2 yawns in Rest Mode → TTS voice inquiry
- Voice response → Whisper STT + two-tier NLP (keyword-first, DeepSeek API fallback)
- Dual interaction paths: yawn-triggered (passive→proactive) + continuous voice commands
- Dynamic Mode / Rest Mode switching with ambient light, sound, UI, and virtual climate
- Cross-platform Python codebase (Windows primary; macOS/Linux untested)

## System Flow

```
MONITORING → YAWN_DETECTED → INQUIRING → LISTENING → TRANSCRIBING → PARSING → CONFIRMING → SWITCHING → MONITORING
```

8 FSM states, non-blocking, with 2 retries on unknown intent.

## Tech Stack

| Layer | Technology |
|---|---|
| Vision | OpenCV, MediaPipe Face Landmarker (478 pts) |
| STT | Whisper `small` (local, offline) |
| NLP | Keyword-first; DeepSeek API fallback |
| TTS | pyttsx3 (SAPI5 on Windows; NSSpeechSynthesizer on macOS; espeak on Linux) |
| State | Thread-safe SharedState + FSM |
| UI | Pygame 1280×720 |
| Audio | sounddevice (VAD + recording) |

> **Note on cross-platform TTS**: pyttsx3 auto-selects the platform backend. Voice quality and behavior differ across Windows (SAPI5), macOS (NSSpeechSynthesizer), and Linux (espeak). This prototype has only been tested on Windows.

## Quick Start

```bash
pip install -r requirements.txt
# Place face_landmarker.task in assets/
# (Optional) Set DEEPSEEK_API_KEY in .env for NLP fallback
python main.py
```

Keyboard shortcuts: `1` Dynamic, `2` Rest, `Y`/`Z` simulate yawn, `Esc` quit.

## Design Principles

- **Inquiry-based, not command-based**: System never auto-executes. Ask → confirm → act.
- **Yawn as cue, not alarm**: Yawns signal relaxation, not danger. Intent ambiguity is resolved through inquiry, not guessing.
- **User agency protected**: Every state transition is gated by user behavior (yawn, voice response).
- **Quiet by default**: Rest Mode is the default. System stays silent unless a meaningful cue is detected.

## Current Limitations

- Single-modality perception (MAR only); eye gaze, head pose, steering behavior not fused
- MAR thresholds are fixed values, not personalized
- Low-light environments reduce MediaPipe landmark stability
- Whisper `small` occasionally mishears short words ("Yes" → "Yinz"), mitigated via keyword dictionary
- pyttsx3 lacks precise speech-done callback
- Desktop prototype; not adapted for in-vehicle hardware

## Project Docs

- [INTERACTION_DESIGN.md](project_docs/INTERACTION_DESIGN.md) — Interaction design rationale
- [SYSTEM_ARCHITECTURE.md](project_docs/SYSTEM_ARCHITECTURE.md) — Engineering architecture
- [PROJECT_JOURNAL.md](project_docs/PROJECT_JOURNAL.md) — Research & development journal
- [FUTURE_WORK.md](project_docs/FUTURE_WORK.md) — Future research directions
- [PROBLEM.md](project_docs/PROBLEM.md) — Known issues and improvement roadmap

## License

[MIT](LICENSE)
