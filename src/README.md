# src/ — planned implementation

> Nothing runs yet. This file fixes the module boundaries so contributions do not collide.
> Every hardware call must sit behind a thin, mockable client class — no `serial.Serial()` at
> module import time, no global state.

## Module layout

```
src/
├─ calib.py          camera intrinsics, homography, tool offset, drift check
├─ servo.py          HID visual servoing on the pointer sprite
├─ scheduler.py      state machine, arbitration, verification, recovery
├─ grbl_client.py    G-code client: move, tap, home, soft limits, e-stop
├─ hid_client.py     ESP32 HID transport (BLE or USB CDC) with heartbeat/reconnect
├─ vision.py         frame grab, cursor detection, element detection adapters
├─ force.py          FSR/HX711 sampling, feature extraction, tap-acceptance classifier
├─ logger.py         JSONL action log (schema in docs/evaluation-protocol.md)
└─ task.py           task YAML loader + assertion DSL
```

## Interfaces (stability contract)

```python
# grbl_client.py
class GrblClient:
    def home(self) -> None: ...
    def move_abs(self, x_mm: float, y_mm: float, feed_mm_min: int = 3000) -> None: ...
    def tap(self, x_mm: float, y_mm: float, press_ms: int = 100) -> None: ...
    def state(self) -> str: ...          # "Idle" | "Run" | "Alarm"
    def emergency_stop(self) -> None: ...

# hid_client.py
class HidClient:
    def connect(self) -> bool: ...
    def move(self, dx: int, dy: int) -> None: ...       # relative
    def click(self, button: str = "left") -> None: ...
    def key(self, code: str) -> None: ...
    def wheel(self, dy: int) -> None: ...
    def healthy(self) -> bool: ...                       # heartbeat within 500 ms

# scheduler.py
class Scheduler:
    def run(self, task: "Task") -> "RunResult": ...
```

## Invariants the code must preserve

1. **Safety first** — any exception path must leave the solenoid de-energised (`M5`) and the
   drivers disabled.
2. **Every action is logged before it is executed**, and again after verification.
3. **No silent retries** — a retry must appear in the log with `fail_label`.
4. **Units are explicit** — all public APIs use `_mm`, `_ms`, `_px` suffixes.
5. **Determinism** — the task seed is passed through to every random choice.

## Testing (once code exists)

- `pytest tests/unit` — pure logic: assert DSL, arbitration scoring, feature extraction.
- `pytest tests/integration` — hardware-in-the-loop, marked `@pytest.mark.hil`, skipped in CI.
- Golden files: recorded HID report streams and GRBL responses for replay without hardware.
