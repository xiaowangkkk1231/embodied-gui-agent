# Contributing

Thanks for taking a look. This project is at the **design/documentation** stage — the highest
value contributions right now are critique and data, not code volume.

## Good first contributions

| Type | What | Where |
|---|---|---|
| Benchmark tasks | YAML files following the template | `tasks/` (create it) |
| Calibration data | chessboard captures + measured homography residuals | issue with a zip |
| Protocol critique | spots where the evaluation is unfair or under-specified | issue |
| Figures | redraw/improve the SVG diagrams, add a wiring diagram | `docs/assets/` |
| Related work | missing papers, or claims that need a correct citation | issue / PR to `docs/related-work.md` |

## Ground rules

1. **Scope**: see [`ETHICS.md`](ETHICS.md). PRs whose purpose is fraud, evasion or
   unauthorised automation of third-party services are rejected. Describe the *experimental
   goal* in the PR body.
2. **No personal data** in commits: no phone numbers, notification bars, IMEI, real account
   screenshots. Use synthetic test screens.
3. **No vendored third-party code** unless required; if you add a dependency, mention its
   license in `LICENSE` → *Third-party notices*.
4. **Assets are text**: prefer SVG over PNG for diagrams so diffs stay readable.

## Workflow

```bash
git clone https://github.com/<your-org>/embodied-gui-agent.git
cd embodied-gui-agent
python scripts/check_assets.py     # must pass before you open a PR
```

- Branch naming: `feat/<topic>`, `fix/<topic>`, `docs/<topic>`.
- Commit messages: imperative, one logical change per commit, reference issues as `#123`.
- PRs: fill the template; CI runs `scripts/check_assets.py` (SVG validity, CSV shape,
  relative links).

## Style

- Documents: Markdown, one H1, section numbers not required, tables over long prose.
- Diagrams: SVG, `viewBox` set, no external fonts, Chinese text allowed with a
  `font-family` fallback list.
- Code (when it lands): Python 3.11+, type hints on public functions, no hidden global state,
  every hardware call behind a thin, mockable client class.

## Reviewing

A PR is merged when: CI is green, the change is scoped, and the ethical section of the PR body
is answered. Expect questions about *why* over *what*.

## Code of conduct

By participating you agree to [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
