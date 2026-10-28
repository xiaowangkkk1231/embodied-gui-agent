# Related Work: Locating the Gap This Paper Addresses

> English | [简体中文](related-work.zh-CN.md)

> Organized around five threads — agents / evaluation / robotic testing / input subsystem / force sensing — with the final section giving this paper's differentiated position.
> Note: citations are given as **author–institution–year + keywords**; complete the DOI/arXiv numbers and verify versions before formal submission.

---

## 1. GUI Agents (Agent Side)

| Work | Core approach | Implication for this study |
|---|---|---|
| **AppAgent** (Tencent, 2023) | Element annotation on screenshots + LLM generating "document-style" operation knowledge, then operating the App step by step from it | Proves that VLMs can do grounding on phones without a DOM; but its execution relies entirely on ADB/accessibility |
| **Mobile-Agent** (Alibaba, 2024) | Multi-agent division of labor: planning, perception, reflection, execution; pure vision | The vision route is viable; it likewise does not solve the problem of injection channels being blocked |
| **Mobile-Agent-v2** | Adds multi-agent collaboration and long-task memory | Long tasks require a "page stack + failure rollback", consistent with this paper's state machine design |
| **AutoGLM** (Zhipu, 2024) | End-to-end phone-operation agent, emphasizing generality | Shows that "general phone agents" have entered the engineering stage, and the execution layer has become the bottleneck |
| **DigiRL** (2024) | Trains mobile agents on real devices/simulators with reinforcement learning | RL training requires large amounts of real-device interaction; a physical platform can provide an interaction channel that **is not blocked** |

**Commonality**: action output is uniformly abstracted as `click/type/swipe` and executed by the system injection channel. **No work treats the "executor" as an object of study** — this is this paper's entry point.

## 2. Datasets and Evaluation

| Resource | Content | Relation to this paper |
|---|---|---|
| **AITW** (Android in the Wild, Google, 2023) | Large-scale real-device operation trajectories (with screenshots + actions) | Can be used to evaluate the decision layer; but the actions are injected via ADB and contain no execution-layer differences |
| **AndroidControl** (Google, 2024) | Instruction–trajectory pairs, covering high- and low-level tasks | Same as above |
| **ScreenSpot** (2024, introduced with SeeClick) | GUI element localization benchmark | Used to measure grounding capability; it is a **confounding variable** for this paper — it must be controlled |
| **AndroidWorld** (Google, 2024) | Interactive Android task environment | Can serve as a reference template for this paper's task suite |
| **Mind2Web / WebArena** (2023) | Web-side agent benchmarks | Methodological borrowing (success assertions, randomization) |

**Gap**: the benchmarks above execute actions at the **software layer**, and their evaluation conclusions do not transfer to "physical execution". **There is no real-device benchmark for "executor comparison".**

## 3. Robotic UI Testing (Hardware Side)

| Project | Form | What can be borrowed |
|---|---|---|
| **Tapster** (open source, GitHub `tapsterbot`, 310★) | 3D-printed parallel/CoreXY arm + capacitive stylus, tapping the phone together with Appium | The **most direct reference** for structure, stylus, and calibration ideas; but it is a "fixed-coordinate script" with no agent and no force feedback |
| **FlexArm** (open source, GitHub `hamlet0168/FlexArm`, 3★) | Robotic arm + camera corner calibration + YAML script orchestration, icon/text recognition and clicking, Windows desktop tool | The **closest finished product** to this paper's goal; proves that "calibration + script + recognition" is feasible. But it is open-loop, has no force channel, has no benchmark protocol, and ships as a binary package |
| **iPhone-Ian** (open source, GitHub `mchdeore/iPhone-Ian`) | A physical device driven by a vision agent to tap an iPhone | The problem statement is almost identical; usable as a "minimal viable device" reference. iPhone only, no measurement layer |
| **Tappy** (TestDevLab, 2017) | Tapster's industrial in-house branch, used for the company's own device testing | Shows that this form factor has entered enterprise test flows; it is likewise an open-loop script |
| **OptoFidelity TouchRobot** (industrial grade) | Multi-axis arm + optical alignment + force control, for touch/HMI performance testing | Shows that "physical touch + force control" is mature in industry; but it is **test equipment** and does not target general tasks |
| Academic **robotic mobile testing** | Uses mechanical devices for press endurance, drop, and touch reliability testing; recent years have seen a series of works on "robots testing mobile App GUIs" (e.g., *Automated Testing of Mobile Applications Using a Robotic Arm*, 2020) | Provides experience in force control and safety design, plus GUI recognition methods; but the goal is to **test devices / test Apps**, not to "use a device to complete tasks" |

**Gap**: existing robotic platforms are all **open-loop scripts or dedicated testing**; no one connects one to a **closed-loop general GUI agent**; no one treats **contact force** as a feedback signal for "the action has taken effect"; and no one quantifies the impact of "physical execution vs software execution" on task success rate.

## 4. Input Subsystem (Mechanism Side)

- **Android input stack**: `InputManagerService` → `InputReader`/`InputDispatcher` → `View.dispatchTouchEvent`; `MotionEvent` carries `source` (`SOURCE_TOUCHSCREEN` / `SOURCE_MOUSE`) and `toolType` (`TOOL_TYPE_FINGER` / `TOOL_TYPE_MOUSE`), and `InputDevice` can be queried for whether it is an external device.
- **HID protocol**: USB HID / Bluetooth HID (BR/EDR HID Profile) and BLE HID (**HOGP**, HID over GATT Profile, Bluetooth SIG specification); the report descriptor determines whether the device is recognized as a mouse, keyboard, digitizer, or gamepad.
- **Injection channels**: `adb shell input`, `AccessibilityService.dispatchGesture`, `uiautomator`.

**Gap**: input-semantic differences (finger vs mouse vs injection) are much discussed in **security/risk control**, but in **agent research** almost no one analyzes them as an "executability" variable. This paper elevates "input semantics" to an experimental variable.

## 5. Force Sensing and Touch

| Direction | Representative | What can be borrowed |
|---|---|---|
| Visuotactile sensing | **GelSight** series (2017–) | High-resolution contact deformation measurement; this paper only needs a low-cost FSR, with a precision requirement an order of magnitude lower |
| Force/impedance control | Force control and compliant control in collaborative robots | Implementation approaches for force limiting, constant-force contact, and collision detection |
| Touchscreen interaction research | Press/force input in HCI | Empirical values for "how much force counts as one tap"; this paper's 2N force limit and 80–120ms hold duration reference such conclusions |

**Gap**: force signals are used in HCI for **human input** and in robotics for **manipulating objects**, but **have not been used as an "action has taken effect" feedback signal for GUI agents** — this is the novelty of this paper's RQ2.

## 6. This Paper's Position (Differentiation)

| Dimension | Existing work | This paper |
|---|---|---|
| Execution mode | Mainly software injection | **Three comparable channels: physical execution + HID + injection** |
| Feedback | Screenshot (vision) | **Vision + contact force, two channels** |
| Executor selection | Fixed implementation | **Online arbitration by task/element** |
| Calibration | One-time manual | **Online self-verification + cross-device-model recalibration** |
| Evaluation | Software-layer benchmark | **Real-device in-the-loop executor benchmark with 60 tasks and 5 control groups** |
| Application | General operation | General operation + accessibility + automated testing |

## 7. Suggested Citation Order (When Writing)

1. Hook: the explosion of phone agents (AppAgent / Mobile-Agent / AutoGLM)
2. Problem: the failure boundary of execution channels (secure keyboard, DRM, controls that recognize only touch)
3. Existing approaches: the limits of software injection → the limits of robotic testing
4. Mechanism: input semantics (source/toolType/HID descriptor)
5. Method: this paper's three channels + force closed loop + arbitration
6. Experiments: 60-task benchmark
7. Discussion: negative results are also valuable (if physical execution shows no advantage → the bottleneck lies in the decision layer)
