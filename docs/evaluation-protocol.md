# Evaluation Protocol and Metric Definitions

> English | [简体中文](evaluation-protocol.zh-CN.md)

> Companion to proposal 01. Objective: make the "physical execution vs. software injection" comparison **reproducible, statistically analyzable, and re-runnable by third parties**.

---

## 1. Task Template (YAML)

```yaml
id: C5-03
category: C5_restricted      # C1_navigation C2_input C3_dialog C4_gesture C5_restricted
title: Enter the payment password in a secure keyboard
app: open_source_demo_app    # self-built / open-source apps only
initial_state:
  activity: PayActivity
  reset: cold_start          # cold_start | warm | specified deep link
goal:
  assert:
    - type: text_present
      value: "支付成功"
    - type: activity_changed
      to: ResultActivity
  max_steps: 15
  timeout_s: 90
randomization:
  - list_order: shuffle      # list item order is randomized
  - start_offset: random     # starting scroll position is randomized
notes: The secure keyboard blocks ADB and accessibility; physical execution is the only available path
```

## 2. Task Suite (5 categories × 12 = 60)

| Category | Task examples (12 each) | Design intent |
|---|---|---|
| **C1 Navigation** | Go back one page, switch bottom Tab, enter a second-level list, open settings, dismiss a permission page | Basic controllability; validates the execution chain |
| **C2 Input** | Type English in a search box, type digits, switch input fields, clear input, submit a form | HID advantage zone |
| **C3 Dialog/Interruption** | Close an interstitial ad, handle network-error retry, allow a permission dialog, handle an upgrade prompt | Robustness and recovery capability |
| **C4 Gesture** | Long-press to open a menu, drag to reorder, two-finger zoom on a map, swipe up/down to refresh, continuous scrolling | Capability boundary (partial failure expected) |
| **C5 Restricted UI** | Secure keyboard input, self-drawn controls that only accept touch, DRM playback control, screenshot-blocked pages (screenshots come out black), pages with accessibility disabled | **Core of RQ1: proof of the value of physical execution** |

> Every task must be decidable by **automated assertion**; otherwise it does not enter the suite.

## 3. Run Protocol

| Item | Specification |
|---|---|
| Cold/warm start | `force-stop` + clear cache before each task; cold start fixed |
| Warm-up | After each device boots, run 3 unscored tasks first to stabilize the system state |
| Repetitions | **5** per task (binary metrics); continuous metrics take the mean of the 5 |
| Randomization | Task order, list order, and starting scroll position are all randomized; the seed is recorded |
| Environment | Fixed illumination (lux-meter reading), fixed battery band (40–80%), airplane mode + fixed WiFi, auto-brightness off |
| Isolation | Only one device runs at a time, to avoid Bluetooth/network interference |
| Human intervention | Manual reset is allowed only after ABORT; the intervention is logged as `human_intervention=true` and counted separately |
| Data retention | Screenshots, raw force-signal sequences, action logs, and video (optional) are all persisted for 30 days |

**Re-run cost**: single device, single group: 60 tasks × 5 runs × 45s average ≈ 3.8 hours; 5 groups ≈ 19 hours per round.

## 4. Metric Definitions

| Metric | Formula / definition |
|---|---|
| **TSR** (task success rate) | `assertion passes / total runs`, binary, strictly judged |
| Strict-subset TSR | C5 only, used for RQ1 |
| **Steps** | `actions / successful tasks` (failed tasks excluded, listed separately) |
| **T_task** | Wall clock from the first OBSERVE to assertion pass/timeout, median + IQR |
| **RetryRate** | `retry actions / total actions` |
| **EffectorMix** | Share of `hid_actions : mech_actions : injected_actions` |
| **ForceAUC** | ROC-AUC of the force classifier on the binary classification of "tap accepted / not accepted" |
| ForceF1 / decision latency | F1@0.5; milliseconds from contact start to verdict output |
| **CalibErr** | RMS reprojection error of calibration points (mm), measured once per boot |
| **RecalTime** | Time from start to CalibErr ≤ 0.5mm after a model change (min) |
| **CrossDeviceDrop** | `(TSR_deviceA − TSR_deviceB) / TSR_deviceA`, measured on 2–3 devices of different brands/resolutions |
| Safety event count | Number of over-force, out-of-bounds, emergency-stop, and screen-indentation (visual inspection) events; **must be 0** |

## 5. Statistical Methods

- Binary (success/failure): paired **McNemar test** (same task, same random seed); report the p value and the effect size (odds ratio).
- Continuous metrics: task-level paired bootstrap (10,000 resamples); report the 95% CI.
- Multi-group comparison: Holm–Bonferroni correction, α = 0.05.
- Reporting convention: `mean ± std` (or median [IQR]), with n and the failure attribution distribution.

## 6. Log Schema (one row per action, CSV / JSONL)

| Field | Type | Description |
|---|---|---|
| `run_id` | str | Unique id of one run (including the seed) |
| `task_id` | str | Corresponding task template |
| `group` | str | B1/B2/B3/B4/Ours |
| `device` | str | Model + OS version + resolution |
| `step` | int | Step index |
| `state` | str | State machine state |
| `action_kind` | str | key/type/scroll/tap/long_press/swipe/drag |
| `effector` | str | hid / mech / adb / a11y |
| `target_bbox` | str | `x,y,w,h` |
| `target_label` | str | Element semantics |
| `latency_ms` | int | End-to-end action latency |
| `force_peak` | float | Newtons (after calibration) |
| `force_impulse` | float | N·ms |
| `contact_ms` | int | Contact duration |
| `verdict` | bool | Post-action verification result |
| `fail_label` | str | See the failure-attribution table in [`scheduler-and-calibration.md`](scheduler-and-calibration.md) |
| `screenshot_before` | str | File path |
| `screenshot_after` | str | File path |
| `human_intervention` | bool | Whether manual intervention occurred |

## 7. Baseline Fairness (mandatory)

1. Compare under **the same task, the same random seed, and the same device**;
2. All groups use the **same grounding model** (otherwise differences are attributed to decision rather than execution);
3. All groups get the **same decision budget** (same step limit, same number of VLM calls);
4. The software injection group uses official APIs (`adb shell input` / `AccessibilityService`), no hacks;
5. Report the **failure attribution distribution**, not just TSR — otherwise "execution is inadequate" and "decision-making is inadequate" cannot be distinguished.

## 8. Expected Result Shape (used to judge whether the experiment is normal)

| Hypothesis | Expectation |
|---|---|
| H1 (RQ1) | On C5, Ours significantly > B1/B2 (e.g., 70% vs 10%), with small gaps on the other categories |
| H2 (RQ2) | Force-classification AUC ≥ 0.85, decision latency ≤ 100ms, 3–10× faster than screenshot verification |
| H3 (RQ3) | Threshold arbitration takes 20–35% less time than a fixed mechanical policy, with a TSR drop < 3% |
| H4 (RQ4) | Cross-device TSR drop < 10%, recalibration ≤ 10min |
| H5 (RQ5) | Gesture coverage is about 60–70%, and C4 TSR is clearly lower than the other categories (expected 30–50%) |

If H1 does not hold (physical execution offers no advantage), this is itself a meaningful negative result — it indicates that the bottleneck lies in the decision layer, and the work should turn toward grounding research.
