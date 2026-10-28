# Hardware

BOM: [`BOM.csv`](BOM.csv) — 44 line items, **¥871** without tools (≈ US$120), 1051 with tools.
All prices are 2026 domestic (CN) street prices and will drift.

## Design constraints

| Constraint | Value | Reason |
|---|---|---|
| Work envelope | 300 × 250 mm | fits a 6.7" phone with margin |
| Z clearance above screen | ~77 mm | solenoid + bracket + spring travel |
| Static tip gap | 1–2 mm | avoid accidental touches |
| Contact force | ≤ 2 N | protect glass, still registered by the digitizer |
| Press duration | 80–120 ms | above the ~40–60 ms recognition window |
| XY resolution | 0.0125 mm/µstep | GT2 20T (40 mm/rev) + 200 step/rev + 1/16 microstep |
| Repeatability target | ±0.1 mm | measured, not nominal |
| Frame | 2020 aluminium + 5 mm acrylic base | stiffness without machining |

## Subsystems at a glance

```
Y rails (2× 8 mm rod)  →  portal side plates  →  X beam (8 mm rod + GT2 belt)
                                                        │
                                                 X carriage + 3D printed plate
                                                        │
                                          bracket → solenoid (12 V, 5 mm stroke)
                                                        │
                                          spring + conductive silicone tip (Ø6)
                                                        │
                                                    phone (fixture)
```

## Motion control

- **Arduino UNO + CNC Shield V3 + GRBL** — cheapest, best-documented 2-axis stack.
- `steps/mm = 200 / 40 × 16 = 80`
- The solenoid is wired to the **spindle PWM** pin through a MOSFET: `M3 S1000` fires,
  `M5` releases. A flyback diode is mandatory.
- Limit switches on X and Y for `$H` homing; soft limits enabled as a second layer.

## Safety wiring

| Element | Rating / note |
|---|---|
| 12 V supply | 5 A, fused at 3 A |
| E-stop | normally-closed, cuts the 12 V rail |
| Logic supply | UNO via USB; separate 5 V LDO for the ESP32 |
| Grounding | single-point common ground; step motor spikes decoupled with 470 µF |
| Watchdog | firmware: 500 ms heartbeat → disable drivers, home |

## Assembly order

1. Base plate → Y rails → side plates (square to 0.1 mm).
2. X beam on Y carriages; belt tension until ~2 mm deflection at 1 N.
3. X carriage + tap head; verify the bracket clears the beam at full travel.
4. Set the static tip gap to 1.5 mm with the spring pre-compressed 1 mm.
5. Wire, fuse, e-stop, then flash GRBL and home.
6. Run 2000 taps on a sacrificial phone and inspect for drift and screen marks.

## Known weak points

- GT2 belt hysteresis: approach every target from the same direction.
- Printed bracket creep under sustained solenoid impact: reprint in PETG or add a metal insert.
- 12 V solenoid heat: keep duty ≤ 20 %, add a 1-minute idle every 10 minutes.

## Bill of materials columns

`序号, 类别, 物料, 规格型号, 数量, 单价CNY, 小计CNY, 用途, 采购渠道`

Subtotal rows and totals are at the bottom of the CSV. When you localise prices, edit only
`单价CNY` and recompute the subtotals.
