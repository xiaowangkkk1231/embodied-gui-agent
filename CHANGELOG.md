# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- "Built with DeepSeek Harness" badge and attribution section in `README.md` and `README.zh-CN.md`.
- **English-labelled versions of all three figures** (`system-architecture.svg`, `three-views.svg`,
  `roadmap-gantt.svg`), so the English README renders English diagrams. The Chinese-labelled
  originals are kept as `*.zh-CN.svg` and used by `README.zh-CN.md`.

### Changed
- `docs/assets/*.svg` renamed to `*.zh-CN.svg` for the Chinese variants; cross-links added in both
  READMEs.

### Planned
- `src/calib.py` — camera intrinsics, homography, tool offset, online re-calibration check
- `src/servo.py` — HID visual servoing on the pointer sprite
- `src/scheduler.py` — state machine, arbitration, post-action verification
- `src/grbl_client.py` — G-code client with soft limits and e-stop handling
- `tasks/` — 60 benchmark task YAMLs (12 per category) plus assertion DSL prototype
- `data/` — example force traces and screenshot pairs (synthetic screens only)
- Wiring diagram and STL-ready mechanical drawings

## [0.1.0] — 2026-10-28

### Added
- `docs/research-proposal.md` — RQ1–RQ5, four-layer system design, 60-task experiment plan,
  ablations A1–A4, risk register, expected contributions.
- `docs/related-work.md` — five research threads (GUI agents, benchmarks, robotic UI testing,
  input subsystem semantics, force/tactile sensing) and the gap statement.
- `docs/scheduler-and-calibration.md` — state machine, action primitives, arbitration
  pseudocode, homography / tool-offset / visual-servo implementation notes, safety limits.
- `docs/evaluation-protocol.md` — task YAML template, run protocol, 13 metric definitions,
  logging schema, statistical tests, baseline-fairness rules.
- `docs/assets/system-architecture.svg` — four-layer architecture with signal flow and the
  three coordinate systems.
- `docs/assets/three-views.svg` — front/top elevation plus tap-head detail drawing.
- `docs/assets/roadmap-gantt.svg` — 12-week plan with six milestones.
- `hardware/BOM.csv` — 44 line items, ¥871 without tools.
- `README.md`, `README.zh-CN.md`, `LICENSE`, `ETHICS.md`, `CONTRIBUTING.md`,
  `CODE_OF_CONDUCT.md`, `CITATION.cff`, CI asset validator.

### Notes
- No runnable code yet: this release is documentation and design only.
