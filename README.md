# Proactive In-Cabin Interaction — An HCI Research Prototype

> 中文版 → [README_CN.md](README_CN.md)

> **What if the cockpit *asked* instead of *acted*?**
>
> This prototype explores a simple but underexamined idea in intelligent cockpit design: the system observes physiological cues, initiates a voice inquiry, and lets the driver decide. No automatic takeovers. No alarms. Just a question.

---

## Research Question

Current Driver Monitoring Systems (DMS) face a structural problem: **physiological signals are inherently ambiguous, yet the system must act on them.** A yawn can mean fatigue, comfort, post-meal drowsiness, or simple stretching. When a system auto-executes based on such ambiguous signals—switching drive modes, issuing alerts, adjusting the cabin—it risks misinterpreting the driver's state and, more importantly, **stripping away their decision authority.**

This raises a core HCI question:

> *Can we shift the cockpit from command-based automation to inquiry-based collaboration, where the system perceives and suggests, but the human always decides?*

---

## Interaction Philosophy

### Inquiry over Automation

The system does not auto-execute. When it detects a meaningful cue (e.g., accumulated yawns suggesting low-arousal relaxation), it asks:

> *"You seem relaxed. Would you like to change to Dynamic Mode?"*

The driver says yes or no. That's it. The system handles **perception + suggestion**; the human retains **decision + confirmation.** This is **Shared Control** extended from the steering wheel to the entire cockpit environment.

### Yawn as Cue, Not Alarm

Conventional DMS treats driver state cues—especially yawns—as deterministic danger signals requiring immediate intervention. We argue this is a category error. Yawns are **contextual, multi-causal physiological events**, not fatigue alarms. Treating them as cues rather than triggers means the system *asks* rather than *acts*, resolving ambiguity through dialogue instead of guessing.

### Preserving Human Decision Authority

Every state transition is gated by explicit user behavior:
- The system *observes* but does not *judge*
- The system *suggests* but does not *force*
- The user feels *noticed*, not *monitored*; *in control*, not *overridden*

Each full interaction cycle—observe → inquire → confirm → execute—functions as a **micro-trust event**: the system proves itself predictable, cancellable, and bounded.

### Quiet by Default

Rest Mode is the default state. The system stays silent unless it accumulates sufficient evidence (≥2 yawn events within the Rest Mode context). This embodies a design stance: **silence over interruption, maintaining the current state over imposing change.**

---

## How It Works (Conceptual)

```
 Driver state cue           System inquiry            Driver response         Outcome
 (yawn detected)    →    "Would you like to        →    "Yes" / "No"     →    Switch / Stay
                          switch modes?"
```

### Two Interaction Paths

| Path | Trigger | Direction | Example |
|---|---|---|---|
| **Path A** | Yawn cue accumulation (≥2 in Rest Mode) | System initiates | System notices relaxation → asks about switching |
| **Path B** | Continuous voice command | Driver initiates | Driver says *"switch to dynamic mode"* anytime |

Path B always overrides Path A. The driver's explicit command takes priority over any system-initiated inquiry. Path A retries at most twice on unrecognized responses, then silently returns to monitoring—avoiding the common assistant failure mode of repeated, escalating prompts.

### A Shared Control Loop

The system runs an 8-state non-blocking loop: Monitoring → Yawn Detected → Inquiring → Listening → Transcribing → Parsing → Confirming → Switching → back to Monitoring. States are gated exclusively by user-relevant events (yawn detected, speech finished, intent parsed), not by system-internal timers or thresholds.

---

## System Overview

```
┌─────────────────────────────────────────────┐
│                  Execution                   │
│     ambient light · sound · climate · UI     │
├─────────────────────────────────────────────┤
│                 Interaction                  │
│          TTS inquiry · STT · NLP             │
├─────────────────────────────────────────────┤
│                    Core                      │
│          Shared State · FSM · Modes          │
├─────────────────────────────────────────────┤
│                 Perception                   │
│     Camera · Face Landmarks · MAR Scoring    │
└─────────────────────────────────────────────┘
```
*(Architecture figure placeholder — see paper/ for system diagrams)*

### Mode Concept

| | Rest Mode *(default)* | Dynamic Mode |
|---|---|---|
| Ambient light | Cool blue | Warm orange |
| Sound | Soothing | High-tempo |
| Virtual climate | 26°C / mild | 18°C / strong |
| Meaning | Driver prefers current comfort | Driver wants a more alerting environment |

The two modes are not simply "sport vs. comfort"—they represent two **user intent paths**: accepting the system's proactive suggestion (Dynamic) or declining to maintain the status quo (Rest).

---

## Interaction Flow

```
Monitoring ──yawn detected (×2)──→ Inquiring ──TTS spoken──→ Listening
                                                                  │
                                                          ┌───────┴────────┐
                                                          ▼                ▼
                                                     "dynamic"          "rest"
                                                          │                │
                                                          ▼                ▼
                                                     Confirming        Confirming
                                                          │                │
                                                          ▼                ▼
                                                     Switch to         Stay in
                                                   Dynamic Mode      Rest Mode
```
*(Interaction flow figure placeholder)*

*(UI screenshot / GIF placeholder — run `python main.py` to capture)*

*(State transition diagram placeholder — see [SYSTEM_ARCHITECTURE.md](project_docs/SYSTEM_ARCHITECTURE.md) for all 8 states)*

---

## Implementation (Minimal)

**Perception**: Camera → MediaPipe Face Landmarks → Mouth Aspect Ratio (MAR) → Exponential-decay yawn scoring (not simple frame-counting; brief landmark jitter does not reset accumulated evidence).

**Voice Pipeline**: pyttsx3 TTS inquiry → 5s microphone recording → Whisper `small` STT → Two-tier NLP (keyword match at 0ms latency; DeepSeek API as fallback).

**State Management**: Thread-safe shared state with 8-state FSM, polled at 60fps by Pygame main loop. Independent threads for camera capture, TTS, continuous voice listening.

**Cross-platform note**: Tested on Windows (pyttsx3 via SAPI5). macOS (NSSpeechSynthesizer) and Linux (espeak) backends are available but untested.

---

## Quick Start

```bash
pip install -r requirements.txt
# Place MediaPipe face_landmarker.task in assets/
# (Optional) Set DEEPSEEK_API_KEY in .env for NLP fallback
python main.py
```

Keyboard: `1` Dynamic, `2` Rest, `Y`/`Z` simulate yawn, `Esc` quit.

---

## Current Limitations (Research Scope)

This is a **desktop research prototype**, not a production system. Known gaps:

- **No user study yet** — design claims about trust, agency, and non-intrusiveness are not yet empirically validated
- **Single-modality perception** — MAR only; eye gaze, head pose, heart rate not fused
- **Fixed thresholds** — not personalized across individuals
- **Desktop simulation** — no real driving task, no steering wheel, no in-vehicle noise environment
- **Whisper `small`** occasionally mishears short words; mitigated via expanded keyword dictionary

See [PROBLEM.md](project_docs/PROBLEM.md) for the full improvement roadmap.

---

## Repository Structure

```
├── paper/              # Academic paper (LaTeX + PDF)
├── project_docs/       # Design docs, architecture, research journal
├── src/                # Source (perception / core / interaction / execution)
├── tests/              # pytest suite (48 tests)
├── assets/             # Model, sounds, images
├── main.py             # Entry point
└── config.py           # Parameters
```

## License

[MIT](LICENSE)
