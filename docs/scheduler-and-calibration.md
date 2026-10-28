# Scheduler, Arbitration, and Calibration (Engineering Implementation Notes)

> English | [简体中文](scheduler-and-calibration.zh-CN.md)

> Companion to the 01 proposal and the 02 architecture diagram. This document gives **directly implementable pseudocode and formulas**, language-agnostic (examples in Python style).

---

## 1. Main State Machine

```
                  ┌──────────────────────────────────────────┐
                  │                                          │
   ┌────────┐   ┌─▼───────┐   ┌────────┐   ┌────────┐   ┌───▼────┐
   │  IDLE  │──▶│ OBSERVE │──▶│ GROUND │──▶│ DECIDE │──▶│   ACT  │
   └────────┘   └─────────┘   └────────┘   └────────┘   └───┬────┘
        ▲                                                    │
        │            ┌──────────┐    ┌────────┐              │
        └────────────│  RECOVER │◀───│ VERIFY │◀─────────────┘
                     └──────────┘    └────────┘
                          │
                     ┌────▼────┐
                     │  ABORT  │  ← safety monitor triggered (excess force / emergency stop / consecutive failures)
                     └─────────┘
```

| State | Entry condition | Exit condition | Timeout |
|---|---|---|---|
| IDLE | Task start / previous step succeeded | An unfinished subgoal exists | — |
| OBSERVE | After any action | Screenshot + force-signal window persisted to disk | 1.0 s |
| GROUND | A screenshot is available | ≥1 candidate element obtained | 2.0 s |
| DECIDE | Candidates are available | `Action` produced | 1.5 s |
| ACT | An Action is available | Effector reports completion | 2.0 s |
| VERIFY | Action completed | success / fail verdict | 1.0 s |
| RECOVER | Verdict is fail | Retry or switch effector | 3 times |
| ABORT | Safety threshold | Manual intervention | — |

**Hard constraints**: maximum steps for a single task (default 20), maximum wall-clock time (default 120s), 3 consecutive failures trigger ABORT.

---

## 2. Action Primitive Interface

```python
@dataclass
class Action:
    kind: str            # key | type | scroll | tap | long_press | swipe | drag
    params: dict         # see the table below
    target: Optional[BBox] = None
    hint: Optional[str] = None   # "hid" | "mech" | None
    timeout_ms: int = 2000

@dataclass
class BBox:
    x: int; y: int; w: int; h: int
    label: str
    responds_to_mouse: bool = True   # estimated from historical success rate, not statically declared
```

| kind | params | Preferred effector | Notes |
|---|---|---|---|
| `key` | `code` (BACK/HOME/APP_SWITCH/ENTER) | HID | System keycode, no localization |
| `type` | `text` | HID | Chinese requires an input method / clipboard |
| `scroll` | `dy` (pixels or notches) | HID | Wheel; most stable on list pages |
| `tap` | `x,y` | Mechanical | Forced to mechanical when the target has `responds_to_mouse=False` |
| `long_press` | `x,y,ms` | Mechanical | 800ms recommended |
| `swipe` | `points[], ms` | HID (drag) | Mechanical requires trajectory planning; prefer HID |
| `drag` | `from,to,ms` | Mechanical | Reordering drags |

---

## 3. Arbiter

Goal: take the Pareto optimum between **success rate** and **latency**.

```python
def choose_effector(a: Action, ctx) -> str:
    # 1) Hard rules: exclude directly when the capability does not match
    if a.kind in ("key", "type", "scroll"):
        return "hid"
    if a.kind in ("tap", "long_press"):
        if ctx.target and not ctx.target.responds_to_mouse:
            return "mech"
        if ctx.mech_busy and ctx.hid_ok:
            return "hid"          # degrade to a visual-servoing click
        if ctx.recent_mech_fail >= 2 and ctx.hid_ok:
            return "hid"
        return "mech"             # default: a real touch is more general
    if a.kind in ("swipe", "drag"):
        return "hid" if a.kind == "swipe" else "mech"
    return "mech"

# Softened version: weighted scoring with online-estimated success rate / latency
# score(e) = w1 * P_success(e, kind) + w2 * P_success(e, target_label)
#            - w3 * E[latency(e)] - w4 * busy_penalty(e)
# Initial weights (1.0, 0.6, 0.004/ms, 0.3), one set trained per task family
```

**Online update**: after each action, maintain a Beta posterior keyed by (kind, target_label, effector), `P_success = α/(α+β)`, sliding window of 200.

---

## 4. Post-Action Verification (VERIFY)

```python
def verify(before, after, expect) -> Verdict:
    if expect.assert_dsl:                 # structured assertions take priority
        return run_assert(expect.assert_dsl, after)
    sim = ssim(before.roi, after.roi)     # structural similarity as fallback
    if sim > 0.98:  return Verdict(False, "no_change")
    if sim < 0.60:  return Verdict(True,  "page_changed")
    return Verdict(True, "element_present") if expect.element in after.elements else Verdict(False, "uncertain")
```

**Failure attribution** (written to the log, for analysis):

| Label | Criterion |
|---|---|
| `decision_error` | The box from grounding has IoU < 0.5 with the manual annotation |
| `execution_error` | The box is correct but nothing changes after the click, and the force signal shows abnormal contact |
| `perception_error` | The screenshot is blurred / occluded / reflecting, and the element is not detected |
| `env_error` | External interruptions such as network, pop-up, or permission |
| `unsupported` | Requires multi-point / gestures, which the hardware does not support |

---

## 5. Calibration

### 5.1 Camera Intrinsics (Offline, Once)

```python
import cv2, numpy as np
# 9x6 checkerboard inner corners, 20mm side length; capture 15 poses
ret, K, dist, _, _ = cv2.calibrateCamera(objp, imgp, gray.shape[::-1], None, None)
# target reprojection error < 0.3 px
```

### 5.2 Pixel → Mechanical Coordinates (Homography H)

```python
def calibrate_homography(pairs):          # pairs: [(u,v), (X_mm, Y_mm)]
    src = np.float32([p[0] for p in pairs])
    dst = np.float32([p[1] for p in pairs])
    H, mask = cv2.findHomography(src, dst, cv2.RANSAC, 3.0)
    err = rms_reprojection(H, src, dst)   # target ≤ 0.5 mm
    return H, err

def px_to_mm(H, u, v):
    p = H @ np.array([u, v, 1.0])
    return p[0]/p[2], p[1]/p[2]
```

**How points are collected**: manual teaching of 4–9 points (the actual positions where the stylus taps on the screen), or automatic collection from a cross array with a known spacing displayed on the screen.

### 5.3 Stylus Offset (tool offset)

```python
# The stylus taps reference point P on the screen once; record the mechanical coordinates (Xm, Ym)
# The camera sees pixel (u, v) at that point → the mapping gives (Xc, Yc)
offset = (Xm - Xc, Ym - Yc)      # subtract it from all subsequent visual targets
```

### 5.4 HID Visual Servoing (Solving the "Relative Coordinates" Problem)

Android draws the mouse cursor on the screen, so a closed loop is possible:

```python
def hid_move_to(u_t, v_t, iters=4, tol=3):
    for _ in range(iters):
        img = grab()
        (u_c, v_c) = detect_cursor(img)          # template-match the cursor arrow
        du, dv = u_t - u_c, v_t - v_c
        if abs(du) <= tol and abs(dv) <= tol:
            return True
        hid.move(dx=gain*du, dy=gain*dv, steps=1) # initial gain 0.8, tuned by convergence
        sleep(0.06)
    return False
```

> If a model does not render the mouse cursor (some custom ROMs), degrade to the open-loop scheme of "return to zero at the four screen corners + fixed step length"; this must be annotated separately in the task suite.

### 5.5 Online Check and Recalibration

```python
def auto_check():
    # Every 30 minutes: the mechanical effector taps baseline points 1, 2, 3 once each, reading the force signal + screenshot to confirm
    errs = [compare(expected, actual) for expected, actual in baseline_points]
    if max(errs) > 0.5:          # mm
        recalibrate()            # re-run 5.2 + 5.3, about 5–10 min
```

### 5.6 Reuse Across Device Models

1. The fixture uses **locating pins + adjustable stop edges**, ensuring the left/bottom edges of the phone align to the same datum;
2. Detect the screen size (resolution + bezel detection) to convert the display area automatically;
3. Recomputing H only requires re-collecting 4 points — target **≤10 min**.

---

## 6. Safety

| Item | Threshold / Policy |
|---|---|
| Maximum stylus contact force | 2 N (closed-loop limiting after FSR calibration) |
| Single press-down duration | ≤ 200 ms |
| Solenoid duty cycle | ≤ 20% (to prevent overheating) |
| Mechanical over-travel | One layer of soft limit + one layer of hard limit |
| Emergency stop | Physical normally-closed button, cuts 12V |
| Watchdog | Main controller gets no heartbeat for 500 ms → power off and return to zero |
| Power sequencing | Logic before power; stepper and BLE supplies filtered separately |

---

## 7. Logging (see [`evaluation-protocol.md`](evaluation-protocol.md) for details)

Each action writes one JSON line: `ts, task_id, step, state, action, target, effector, latency_ms, force_peak, force_impulse, verdict, fail_label, screenshot_before, screenshot_after`.
