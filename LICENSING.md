# Licensing

This repository mixes code, prose and hardware designs, so no single license covers all of it.
The file [`LICENSE`](LICENSE) contains the plain **MIT** text, which applies to software.
Everything else is licensed as described below.

GitHub reads only `LICENSE` for the sidebar badge, which is why the split lives here instead of
inside that file (mixing the two made GitHub report `NOASSERTION`).

## Per-directory map

| Path | License | Notes |
|---|---|---|
| `src/`, `scripts/` | **MIT** | see [`LICENSE`](LICENSE) |
| `docs/`, `README*.md`, `ETHICS.md`, `CONTRIBUTING.md`, `CHANGELOG.md` | **CC BY 4.0** | <https://creativecommons.org/licenses/by/4.0/> |
| `docs/assets/*.svg` | **CC BY 4.0** | figures; attribution required |
| `hardware/` (BOM, future CAD/STL) | **CERN-OHL-S v2** | <https://ohwr.org/cern_ohl_s_v2.txt> |

If you reuse the hardware design, CERN-OHL-S v2 requires that modifications to the design files be
shared under the same license. Building a rig for yourself is unrestricted.

## Third-party notices

The repository references, but does not bundle, the following projects. Their licenses apply when
you install or copy them:

- **GRBL** — GPL-3.0 (firmware for the Arduino UNO motion controller)
- **Arduino core / ESP32 Arduino core** — LGPL-2.1 / Apache-2.0
- **OpenCV** — Apache-2.0
- **ESP32 BLE HID libraries** (e.g. `ESP32-BLE-Mouse`, `ESP32-BLE-Keyboard`) — MIT

The MIT / CC BY / CERN-OHL split above does not relicense any third-party code.

## Citing

Metadata lives in [`CITATION.cff`](CITATION.cff); GitHub renders a "Cite this repository" button
from it.
