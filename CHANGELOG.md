# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Nothing yet. Planned for the next release — see the roadmap in [`README.md`](README.md):

- `src/calib.py` — camera intrinsics, homography, tool offset, online re-calibration check
- `src/servo.py` — HID visual servoing on the pointer sprite
- `src/scheduler.py` — state machine, arbitration, post-action verification
- `src/grbl_client.py` — G-code client with soft limits and e-stop handling
- `tasks/` — 60 benchmark task YAMLs (12 per category) plus assertion DSL prototype
- `data/` — example force traces and screenshot pairs (synthetic screens only)
- Wiring diagram and STL-ready mechanical drawings

## [0.1.0] — 2026-10-28

First public release: the **design and documentation package**. No runnable code yet.

### Added

**Documents (bilingual — English default, Simplified Chinese as `*.zh-CN.*`)**

- `docs/research-proposal.md` — RQ1–RQ5, four-layer system design, 60-task experiment plan,
  ablations A1–A4, risk register, expected contributions.
- `docs/evaluation-protocol.md` — task YAML template, run protocol, 13 metric definitions, logging
  schema, statistical tests (McNemar / paired bootstrap), baseline-fairness rules.
- `docs/scheduler-and-calibration.md` — state machine, action primitives, arbitration pseudocode,
  homography / tool-offset / visual-servo notes, safety limits.
- `docs/related-work.md` — five research threads (GUI agents, benchmarks, robotic UI testing, input
  subsystem semantics, force/tactile sensing), the gap statement, and open-source prior art
  (Tapster, FlexArm, iPhone-Ian, Tappy, OptoFidelity TouchRobot).

**Figures (SVG, English + `*.zh-CN` variants)**

- `docs/assets/system-architecture.svg` — four-layer architecture with signal flow and the three
  coordinate systems.
- `docs/assets/three-views.svg` — front elevation, top view, tap-head detail, parts legend.
- `docs/assets/roadmap-gantt.svg` — 12-week plan with milestones M1–M6.

**Hardware and repository scaffolding**

- `hardware/BOM.csv` — 44 line items, ¥871 without tools (¥1051 with tools).
- `README.md` / `README.zh-CN.md`, `ETHICS.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`,
  `CITATION.cff`, `LICENSING.md`, MIT `LICENSE`.
- `scripts/check_assets.py` + GitHub Actions workflow: SVG well-formedness, CSV column shape,
  relative-link existence, `CITATION.cff` required fields.
- Issue templates (`bug_report`, `protocol_critique`) and a PR template with a mandatory ethics
  statement.

### Notes

- This release is **documentation and design only**; `src/` contains interface contracts, not code.
- Licensing is split: MIT for code, CC BY 4.0 for documents and figures, CERN-OHL-S v2 for hardware.
  See [`LICENSING.md`](LICENSING.md).
- Intended use is GUI-agent research, accessibility and automated mobile-app testing. Reward
  farming, engagement fraud and anti-fraud evasion are explicitly out of scope — see [`ETHICS.md`](ETHICS.md).
