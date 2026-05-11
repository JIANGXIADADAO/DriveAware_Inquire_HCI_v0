# Proactive In-Cabin Interaction — Driver State Awareness Research Prototype

> 智能座舱 HCI 原型：系统主动询问，驾驶员做决定。不强制，不告警。

---

## What This Is

一个研究原型，探索智能座舱中 **proactive interaction** 与 **shared control** 的交互范式。系统通过面部感知检测驾驶员哈欠（作为低唤醒度放松状态的 cue），主动以语音发起询问，由驾驶员选择切换至 Dynamic Mode 或 Rest Mode，座舱环境随之联动。

核心命题：**系统承担感知与建议，决策权始终在人。**

---

## 核心功能

- 面部 landmark 实时 MAR 计算 + 指数衰减评分 → 哈欠检测
- 在 Rest Mode 下累积 2 次哈欠 → TTS 主动询问
- 驾驶员语音回应 → Whisper STT + 关键词/NLP 意图解析
- Dynamic Mode / Rest Mode 双模式切换（环境光、音效、UI、虚拟空调）
- 持续语音指令监听（不需要等哈欠，随时可以说 "switch to rest mode"）

---

## 系统流程

```
MONITORING → YAWN_DETECTED → INQUIRING → LISTENING → TRANSCRIBING → PARSING → CONFIRMING → SWITCHING → MONITORING
```

8 个状态，每个转换由标志位驱动，FSM 不阻塞主线程。2 次未知意图重试。

---

## 技术栈

| 层次 | 选型 |
|---|---|
| 视觉 | OpenCV, MediaPipe Face Landmarker (478 pts) |
| STT | Whisper `small`（本地离线） |
| NLP | 关键词优先；Fallback DeepSeek API |
| TTS | pyttsx3（Windows SAPI5） |
| 状态 | 线程安全 SharedState + FSM |
| UI | Pygame 1280×720 |
| 音频 | sounddevice（VAD 连续监听 + 录音） |

---

## 设计亮点

- **Inquiry-based, not command-based**：系统不自动执行。询问 → 确认 → 执行。
- **Yawn as cue, not alarm**：哈欠不是危险信号，是放松线索。意图不确定性通过询问解决，而非系统猜测。
- **Dual interaction path**：哈欠触发流程 (passive → proactive) + 持续语音指令 (active)
- **Keyword-first NLP**：90% 场景零延迟关键词命中，API 仅作 fallback
- **Decay-scoring detector**：短暂 landmark 抖动不会重置累积分数

---

## Current Limitations

- 单模态感知（仅 MAR），未融合眼动/头姿/方向盘行为
- MAR 阈值为固定值，未做个性化标定
- 低光照环境下 MediaPipe landmark 稳定性不足
- Whisper `small` 对短单词偶有误识别（"Yes"→"Yinz", "Rest"→"Res"）
- pyttsx3 无精确 speech-done 回调
- PC 桌面原型，未适配车载硬件

---

## Quick Start

```bash
pip install -r requirements.txt
# 将 face_landmarker.task 放入 assets/
# (可选) 在 .env 中配置 DEEPSEEK_API_KEY
python main.py
```

键盘：`1` Dynamic, `2` Rest, `Y`/`Z` 模拟哈欠, `Esc` 退出.

---

## 文档索引

- [INTERACTION_DESIGN.md](INTERACTION_DESIGN.md) — 交互设计逻辑
- [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) — 系统工程架构
- [PROJECT_JOURNAL.md](PROJECT_JOURNAL.md) — 研究开发日志
- [FUTURE_WORK.md](FUTURE_WORK.md) — 扩展方向
