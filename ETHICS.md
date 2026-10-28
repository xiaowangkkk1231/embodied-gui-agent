# Ethics, Safety and Acceptable Use

This document is part of the repository, not boilerplate. If you fork or reuse this
project, keep it.

## 1. What this project is for

- **GUI-agent research**: studying how embodied execution compares with software injection.
- **Accessibility**: single-switch or assistive interaction with a phone.
- **Automated testing**: hardware-in-the-loop UI regression testing on real devices.
- **Education**: a practical mechatronics + vision + Android-input project.

## 2. Explicitly out of scope

The following are **not** supported, and the maintainers will not provide guidance,
code or tuning for them:

1. **Reward / ad-revenue farming.** Using the rig to generate fake engagement, watch
   time, ad impressions or "coins" on any commercial app. This is ad fraud and, in many
   jurisdictions, a criminal matter (fraud, computer-misuse or unfair-competition statutes).
2. **Anti-fraud evasion.** Making device input, timing or behaviour look human in order to
   defeat a platform's risk controls. This repository studies *what the platform observes*;
   it does not optimise *how to hide from it*.
3. **Bypassing authentication or payment confirmations** on devices you do not own.
4. **Click farms / phone walls** operated for third parties.

If you are unsure whether your use is acceptable, open an issue and describe the
*experimental goal*, not the target app.

## 3. Experiments must use

- applications you wrote (a demo/test app), open-source apps, or vendor test devices;
- your own hardware and accounts;
- non-personal data only. No scraping of other users' content, no collection of device
  identifiers belonging to third parties.

## 4. Physical safety

| Risk | Control |
|---|---|
| Screen damage from over-force | contact force limited to **2 N**, spring-damped tip, soft silicone, 80–120 ms press |
| Pinched fingers / crush | soft travel limits + physical e-stop cutting the 12 V rail |
| Stepper runaway | watchdog (500 ms heartbeat) → power off + home |
| Solenoid overheating | duty cycle ≤ 20%, freewheel diode |
| Eye strain / photophobia from ring light | diffused light, adjustable intensity |
| Electrical | fused 12 V input, separated logic/power rails, common ground only at one point |

**Do not** run the rig unattended for long periods without the force limit verified by a
calibration measurement.

## 5. Data and privacy

- Clicks, screenshots and force traces are recorded for evaluation. Capture only your own
  test accounts.
- If you publish datasets, strip status-bar content (notifications, phone numbers, IMEI),
  and prefer synthetic test screens.
- Force traces and screenshots can identify a device model; document this in your dataset
  card.

## 6. Responsible disclosure

If you discover that this design or its software can be misused in a way not covered here,
or you find a security issue in the tooling, contact the maintainers privately before
publishing.

## 7. Enforcement

Maintainers may close issues, reject PRs or block contributors whose stated purpose is
fraud, evasion, or unauthorised automation of third-party services.
