# System Architecture

> 工程视角的系统拆解：模块划分、数据流、状态流、API 交互。

---

## 1. 四层架构

```
┌────────────────────────────────────────────────────┐
│  Execution Layer                                   │
│  cockpit_app.py  cockpit_ui.py  ambient_light.py   │
│  sound_manager.py  climate_display.py              │
└────────────────────────┬───────────────────────────┘
                         ↑
┌────────────────────────────────────────────────────┐
│  Interaction Layer                                 │
│  tts_engine.py  stt_engine.py  nlp_parser.py       │
│  audio_recorder.py  voice_listener.py              │
└────────────────────────┬───────────────────────────┘
                         ↑
┌────────────────────────────────────────────────────┐
│  Core Layer                                        │
│  shared_state.py  state_machine.py  modes.py       │
└────────────────────────┬───────────────────────────┘
                         ↑
┌────────────────────────────────────────────────────┐
│  Perception Layer                                  │
│  camera.py  face_mesh.py  mar.py  yawn_detector.py │
└────────────────────────────────────────────────────┘
```

---

## 2. 感知层 — Fatigue Detection Pipeline

```
Camera (15fps) → Face Landmark (MediaPipe 478 pts) → MAR Calculation → Yawn Scoring
```

### MAR 计算 (`mar.py`)

六点法 inner lip contour（MediaPipe landmark indices）：
- Width: p1(61) ↔ p5(291)
- Height: average of 3 vertical pairs — (p2-p8), (p3-p7), (p4-p6)
- Formula: `MAR = (d1 + d2 + d3) / (3.0 × width)`

闭口 MAR ≈ 0.2–0.3，张口哈欠 MAR ≈ 0.5–0.8。

### 哈欠检测 (`yawn_detector.py`)

指数衰减评分模型，参考 AttentionScorer（e-candeloro/Driver-State-Detection）：
- MAR > threshold: `score += growth`（growth = 1.0 / SUSTAINED_FRAMES × 1.2）
- MAR < threshold: `score ×= 0.85`（单帧仅损失 15% 证据）
- score ≥ 1.0 → yawn triggered, score 归零, cooldown 启动

优势：不要求严格连续帧。短暂 landmark 抖动不会归零累积证据。

### 配置参数

| 参数 | 值 | 含义 |
|---|---|---|
| MAR_THRESHOLD | 0.48 | 张口阈值 |
| MAR_SUSTAINED_FRAMES | 20 | ~1.3s @ 15fps 持续张口 |
| MAR_COOLDOWN_SECONDS | 2.0 | 两次哈欠间最短间隔 |

---

## 3. 交互层 — Voice Interaction Pipeline

### 3.1 哈欠触发路径

```
FSM: LISTENING
  → AudioRecorder.record(duration=5.0s, shared_state)
  → STTEngine.transcribe(audio, boost=3.0)
  → NLPParser.parse_intent(transcript)
  → FSM: TRANSCRIBING → PARSING → CONFIRMING / INQUIRING(retry)
```

录音模块 (`audio_recorder.py`) 启动时自动检测最佳麦克风设备，测试多种采样率/通道组合，选择 RMS 最高的配置。

### 3.2 持续语音监听路径

独立线程 (`voice_listener.py`)，基于 VAD (Voice Activity Detection)：
- 0.2s chunk → RMS 计算 → 与自适应阈值比较
- 自适应阈值 = max(base_threshold, noise_floor × 3.0)
- Noise floor 通过 EMA 持续追踪（仅在不主动监听时更新，避免语音抬高噪声基线）
- 3 个连续 speech chunk → 开始录音 → 15 个连续 silence chunk → 停止 → STT + NLP

### 3.3 STT — Whisper

- 模型：`small`（~244M 参数），本地推理
- 音频 boost 3.0x（提升安静环境下的识别率）
- 已知问题：`small` 模型对短单词存在幻读（"Yes"→"Yinz", "Rest"→"Res"），通过关键词词典扩展缓解

### 3.4 NLP — 两层解析

```
transcript
  → _keyword_parse()     # 关键词匹配，0ms 延迟
  → [hit] → return intent
  → [miss] → _api_parse()  # DeepSeek API fallback，~800ms
  → [API fail] → "unknown"
```

关键词列表包含：
- Yes-like: yes, yeah, yep, ok, sure, absolutely, yinz*, yass* ...
- No-like: no, nope, nah, rest, relax, calm, comfort, res*, ress* ...

（`*` = Whisper 常见误识别词）

DeepSeek API prompt：分类为 "dynamic", "rest", "unknown"，temperature=0.0，max_tokens=10，3 次重试。

---

## 4. 核心层 — State Management

### SharedState (`shared_state.py`)

单一数据总线，所有线程（Camera, TTS, VoiceListener, FSM/UI）通过它通信。`threading.Lock` 保护所有读写。

关键字段：
- `system_state` — FSM 当前状态（枚举）
- `yawn_detected`, `yawn_count` — 哈欠信号
- `last_intent`, `last_transcript` — NLP 解析结果
- `tts_done`, `worker_done` — 状态转换门控标志
- `voice_intent`, `voice_transcript` — 持续语音指令
- `active_mode` — 当前座舱模式（"rest"/"dynamic"）
- `mic_level`, `debug_mar`, `face_detected`, `camera_frame` — 调试/可视化

### FSM (`state_machine.py`)

8 个状态，纯函数 `update(shared)`，每帧由 Pygame 主循环调用：

```
MONITORING → YAWN_DETECTED → INQUIRING → LISTENING → TRANSCRIBING → PARSING → CONFIRMING → SWITCHING → MONITORING
```

每个状态的转换条件：
- MONITORING: `yawn_detected and count >= 2 and active_mode == "rest"`
- YAWN_DETECTED: 无条件（去抖闸门，下一帧直接转 INQUIRING）
- INQUIRING: `tts_done`
- LISTENING: `worker_done`（录音结束）→ TRANSCRIBING; `tts_done`（超时）→ INQUIRING
- TRANSCRIBING: `worker_done`（STT+NLP 完成）→ PARSING
- PARSING: `worker_done` → intent in ("dynamic","rest") → CONFIRMING; intent="unknown" → INQUIRING(retry) or MONITORING(exhausted)
- CONFIRMING: `tts_done`
- SWITCHING: 无条件 → MONITORING

重试逻辑：最多 2 次未知意图重试，第三次放弃回到 MONITORING。

### Modes (`modes.py`)

两个 `CockpitMode` dataclass 实例，定义颜色、音效文件、UI 叠加图、虚拟空调参数。

---

## 5. 执行层 — UI & Environment Simulation

### Pygame 主循环 (`cockpit_app.py`)

每帧执行顺序：
1. `fsm_update(shared)` — FSM 状态转换
2. `_handle_fsm_actions()` — 触发 TTS / voice pipeline
3. 检查 `shared.last_intent` — 执行模式切换（哈欠触发路径）
4. 检查 `shared.pop_voice_intent()` — 执行模式切换（持续语音指令路径）
5. `ambient_light.update()` — 环境光渐变
6. `cockpit_ui.render()` — 渲染 UI + 面部预览

### 环境光渐变 (`ambient_light.py`)

每帧 8 RGB step 平滑过渡到目标颜色，避免突兀切换。

### UI 组件 (`cockpit_ui.py`)

- 主标题（模式名称）
- 环境光颜色标签
- 虚拟空调参数（温度 / 风速 / 送风方向）
- 面部预览小窗（320×240，左下角，含 MAR 值和 Face 状态叠加）
- 麦克风电平指示
- 底部按键提示

---

## 6. 线程模型

```
Main Thread (Pygame UI loop, FSM update, 60fps)
Camera Thread (15fps capture + detection)
TTS Thread (queue-based speak, blocking runAndWait)
VoiceListener Thread (continuous VAD + STT + NLP)
_voice_pipeline Thread (one-shot, created per yawn-triggered interaction)
Watchdog (每 60 帧检查 camera/tts/listener 线程健康，自动重启最多 3 次)
```

---

## 7. 当前架构 Limitations

- **无消息总线**：线程间通信依赖 SharedState + polling（FSM 每帧读取标志位），缺乏事件驱动机制。增加线程或事件类型时复杂度非线性增长
- **TTS 无精确回调**：pyttsx3 `runAndWait()` 阻塞 TTS 线程，FSM 通过 `tts_done` 标志位判断完成。无法精确知道播报何时结束，存在竞态窗口
- **Whisper 模型加载在主线程**：`stt.load()` 在启动阶段阻塞（~5–15s 取决于硬件），期间 UI 不可交互
- **FSM 与 UI 耦合在 Pygame 循环中**：FSM 逻辑在每个 Pygame 帧执行 but 状态转换的 action（TTS、录音）在单独的 `_handle_fsm_actions()` 中管理，两个函数有隐式时序依赖
- **无配置热加载**：所有参数在 `config.py` 中硬编码，运行时不可调
