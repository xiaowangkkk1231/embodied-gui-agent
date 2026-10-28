# Embodied GUI Agent: Physical Robotic-Arm Execution and Force-Vision Closed Loop for Real Devices

> English | [简体中文](research-proposal.zh-CN.md)

> Research proposal v1.0 ｜ 2026-10-28 ｜ Companion files: [system architecture](assets/system-architecture.svg) · [roadmap](assets/roadmap-gantt.svg) · [BOM](../hardware/BOM.csv) · [scheduler & calibration](scheduler-and-calibration.md) · [evaluation protocol](evaluation-protocol.md) · [related work](related-work.md)

---

## 0. Abstract

Existing mobile GUI Agents (AppAgent, Mobile-Agent, AutoGLM, etc.) almost all execute actions through software injection (ADB / accessibility service / uiautomator). Such approaches fail outright on secure keyboards, payment pages, DRM video, and controls that only accept real touch, and they cannot verify real-device usability outside an emulator.

This proposal studies **embodied execution**: a real-device-in-the-loop (hardware-in-the-loop) system composed of "visual perception + large-model decision making + physical robotic-arm execution + HID channel assistance", and it introduces **contact force signals** as a feedback channel that software Agents do not have. The core claims are:

1. **Executability extension**: physical execution can cover the interface categories where software injection fails;
2. **Force-vision closed loop**: time-domain contact force features can self-supervisedly determine "whether a tap is accepted by the system", with better accuracy and latency than pure visual judgment;
3. **Effector arbitration**: under the dual objectives of latency and success rate, the optimal dispatch policy between HID and the robotic arm can be quantified and yields significant gains;
4. **Online self-calibration**: enables reuse of the same rig across device models, reducing recalibration cost from hours to minutes.

Expected outputs: a reproducible evaluation protocol and task suite, an open-source hardware platform design, and several publishable experimental conclusions.

---

## 1. Background and motivation

### 1.1 Execution bottlenecks of existing GUI Agents

| Bottleneck | Manifestation | Impact |
|---|---|---|
| Injection channel blocked | Secure keyboards, payment pages, games, and DRM players do not respond to `adb input` / accessibility | The task fails permanently and cannot be bypassed |
| Semantic non-equivalence | Injected events lack `TOOL_TYPE_FINGER` and carry no pressure/area | Controls that only recognize touch ignore them outright |
| Not reproducible on real devices | High success rate in sandbox/emulator, significantly lower on real devices | Poor external validity of research conclusions |
| No physical feedback | The Agent can only "see" the result and cannot sense "whether the tap landed" | Failure detection relies on expensive vision |

### 1.2 Why "embodied" is worth studying

- **Only pathway**: some interfaces are unreachable at the software layer, and physical touch is the only legitimate input;
- **New sensing modality**: contact force and contact timing are information that the software channel does not have;
- **Reproducible platform**: a real-device-in-the-loop evaluation base that can serve three lines of research: GUI Agents, accessibility, and App testing;
- **Engineering value**: "robotized UI testing" by phone vendors/App vendors already has industrial demand (e.g., OptoFidelity TouchRobot, open-source Tapster).

### 1.3 Compliance boundaries of this document

This study uses **self-built test Apps, open-source applications, and vendor test devices** as experimental subjects; it does not design experiments against the revenue/reward mechanisms of any commercial application; it does not collect real user data; the robotic arm limits force to protect the screen. The technology is the same, the objectives differ, and the nature is entirely different.

---

## 2. Research questions

| ID | Question | Hypothesis | Metric |
|---|---|---|---|
| **RQ1** | Does embodied execution expand the reachable task suite of GUI Agents? | On the "touch-only" category, physical execution achieves a significantly higher success rate than software injection | TSR difference, distribution of failure reasons |
| **RQ2** | Can contact force self-supervisedly determine whether a tap is accepted? | Force time-domain features (peak, impulse, rebound time) separate "valid tap/invalid tap" | AUC, F1, decision latency |
| **RQ3** | What is the optimal dispatch policy between HID and the robotic arm? | Dispatching by action category outperforms fixed dispatch on "time-success rate" | Pareto frontier, mean task duration |
| **RQ4** | Can online self-calibration support cross-model reuse? | Automatic recalibration can hold the error within ±0.5mm at a cost of < 10min | Calibration error, recalibration time, cross-model TSR drop |
| **RQ5** | How many touch gestures can single-finger mechanical execution + HID cover? | Covers about 60–70%, and the gap can be approximated with HID keyboard/mouse and trajectory planning | Gesture coverage matrix, approximation success rate |

---

## 3. System design

See [`assets/system-architecture.svg`](assets/system-architecture.svg). Four-layer structure:

### 3.1 Perception layer
- **Vision**: a USB camera looks down at the phone screen (1080p, manual focus, fixed fill light), frame rate ≥ 15fps;
- **Screen understanding**: screenshot → OCR/VLM grounding (outputs element boxes and semantic labels) → coordinate mapping;
- **Force sensing**: an FSR thin-film pressure sensor or a miniature load cell is mounted behind the tap head, sampling ≥ 200Hz, raw ADC sequence;
- **State variables**: cursor position (visual detection of the mouse arrow), axis position (GRBL status), connection status (BLE heartbeat).

### 3.2 Decision layer
- **Planner**: the LLM decomposes the task into a sequence of subgoals;
- **Grounding**: VLM/OCR resolves subgoals into screen coordinates and element types;
- **Verifier**: post-action screenshot comparison (structural similarity + presence of key elements) yields success/fail;
- **Memory**: page stack, attempted actions, failure reasons, used for retry and rollback.

### 3.3 Execution layer (action primitives + arbitration)

| Primitive | Preferred effector | Alternative |
|---|---|---|
| `key(code)` back/Home/switch page | HID keyboard | — |
| `scroll(dy)` | HID scroll wheel | mechanical drag (inefficient) |
| `type(text)` | HID keyboard | — |
| `tap(x,y)` | mechanical tap head | HID visual servoing (if the target accepts a mouse) |
| `long_press(x,y,ms)` | mechanical tap head | HID hold |
| `swipe(points)` | HID drag / mechanical trajectory | — |
| `multi_touch` | not supported (coverage gap) | declared limitation |

Arbiter inputs: action type, target element properties (whether it responds to a mouse), current latency budget, success rate of the previous effector → outputs the effector and parameters.

### 3.4 Feedback layer: force-vision closed loop
- At the instant of the tap, capture a force signal window [t-50ms, t+150ms];
- Features: peak force, rising-edge slope, impulse, rebound time, contact duration, secondary impact;
- Label source: screenshot verification results (automatic labeling) + manual spot-checking;
- Target: AUC ≥ 0.85 and decision latency ≤ 100ms, so that failures can be detected quickly and retried without taking a screenshot.

---

## 4. Experimental design

### 4.1 Task suite (5 categories × 12 tasks = 60 tasks)

| Category | Example | Design intent |
|---|---|---|
| C1 Navigation | back, switch tab, enter a second-level page | basic controllability |
| C2 Input | search-box entry, form filling | where HID has the advantage |
| C3 Popups/interruptions | permission dialog, interstitial ad, network-error retry | robustness |
| C4 Gestures | long-press menu, drag-to-reorder, two-finger zoom | coverage gap |
| C5 Restricted interfaces | secure keyboard, touch-only controls, DRM playback page | **RQ1 core** |

Each task specifies: initial state, success criterion (structured assertions), maximum step count, and randomization items (list order, starting page).

### 4.2 Control groups

| Group | Execution method | Purpose |
|---|---|---|
| B1 | ADB `input tap/swipe` | industrial baseline |
| B2 | accessibility service injection | mainstream Agent baseline |
| B3 | pure HID | low-cost peripheral baseline |
| B4 | pure mechanical (no visual servoing) | mechanical baseline |
| **Ours** | hybrid + force feedback + arbitration | main method |

### 4.3 Metrics

| Metric | Definition |
|---|---|
| **TSR** | task success rate (strict assertions passed) |
| Steps | mean number of action steps |
| T_task | mean wall-clock duration |
| RetryRate | retries / number of actions |
| EffectorMix | share of actions per effector |
| ForceAUC / F1 | force classifier performance |
| CalibErr | reprojection error of calibration points (mm) |
| RecalTime | recalibration time after a device-model change (min) |
| CrossDeviceDrop | relative TSR drop across device models |

### 4.4 Ablation

- A1: remove force feedback (visual verification only);
- A2: remove visual servoing (HID moves blindly with a fixed step size);
- A3: fixed arbitration vs threshold arbitration vs learned arbitration;
- A4: offline calibration only vs online self-calibration.

### 4.5 Statistics

- Repeat each task 5 times and report mean ± std;
- Use McNemar's test (paired) for binary outcomes and bootstrap 95% CI for continuous metrics;
- Significance threshold α = 0.05; report effect sizes;
- Randomize task order and initial state; blind evaluation (the verifier asserts automatically).

---

## 5. Timeline

See [`assets/roadmap-gantt.svg`](assets/roadmap-gantt.svg). 12 weeks, 7 workstreams in parallel:

| Week | Milestone |
|---|---|
| W1–2 | baseline and environment ready, B1/B2 running, baseline TSR table |
| W3–4 | mechanical platform assembly + visual calibration, tap accuracy ±0.3mm |
| W5–6 | HID channel + visual servoing convergence |
| W7–8 | arbiter + closed-loop verification + recovery |
| W9–10 | 60-task suite completed, 5 control groups |
| W11 | ablation experiments + force classifier training |
| W12 | paper/report + reproduction package (code, BOM, calibration scripts, data) |

---

## 6. Risks and contingencies

| Risk | Probability | Impact | Contingency |
|---|---|---|---|
| VLM grounding errors dominate failures | High | Confounds the RQ1 conclusion | Use a manually annotated subset to separate "decision errors" from "execution errors" |
| Mechanical calibration drift | Medium | Long-running tasks fail | Automatically check one reference point every 30 minutes and recalibrate when it exceeds the threshold |
| BLE disconnection | Medium | Missing data | Heartbeat + automatic reconnection + marking of failed samples |
| Screen glare/insufficient brightness | Medium | Unstable vision | Fixed fill light + fixed exposure + polarizing filter |
| Insufficient time | Medium | Incomplete experiments | Reduce the task suite to 30 (6 per category), keeping C5 |
| Ethics review | Low | Cannot publish | Use only open-source Apps/self-built Apps, with an ethics statement attached |

---

## 7. Expected contributions

1. **A real-device-in-the-loop embodied GUI Agent platform** (hardware design + open-source code + calibration procedure);
2. **A tap-decision method based on the force-vision closed loop** and a public dataset (force signals + screenshots + labels);
3. **An effector arbitration policy** and its empirical conclusions (when to use physical execution and when not to);
4. **An evaluation protocol with 60 tasks and 5 control groups** that later work can reuse;
5. A quantitative answer to the question "whether physical execution is necessary".

---

## 8. Deliverable list

| No. | File | Content |
|---|---|---|
| 1 | [`research-proposal.md`](research-proposal.md) | this document |
| 2 | [`assets/system-architecture.svg`](assets/system-architecture.svg) | four-layer architecture, signal flow, coordinate systems |
| 3 | [`assets/roadmap-gantt.svg`](assets/roadmap-gantt.svg) | 12-week plan |
| 4 | [`hardware/BOM.csv`](../hardware/BOM.csv) | mechanical / electrical / HID / sensing / vision |
| 5 | [`scheduler-and-calibration.md`](scheduler-and-calibration.md) | state machine, arbitration pseudocode, calibration, visual servoing |
| 6 | [`evaluation-protocol.md`](evaluation-protocol.md) | task templates, assertions, log schema, statistics |
| 7 | [`related-work.md`](related-work.md) | five threads and the gaps |

Every file also exists in Simplified Chinese as `*.zh-CN.md` / `*.zh-CN.svg`.
