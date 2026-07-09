# v4.0.0-rc.1 readiness checklist (US0109 / CR0198)

Cutting `v4.0.0-rc.1` is a checklist read, not a judgement call. Every gate below has a live
check command; recompute them immediately before tagging (do not trust a stale number). The tag
cut, freeze lift, and push to consuming projects are an explicit operator action once ALL gates
read green.

> **Computed:** 2026-07-09 · re-run each check before the tag.

| Gate | Live check | State (2026-07-09) |
| --- | --- | --- |
| Portable gate green | `scripts/gate.py --root .` | GREEN - `gate: PASS` |
| Version homed at 4.0.0-rc.1 | `tools/check_versions.py --strict` | GREEN - consistent (core 4.0.0) |
| Migration rehearsed on 2 real projects | `sdlc-studio/reviews/v4-migration-rehearsal.md` | GREEN - rehearsed; BG0070 found, fixed, re-rehearsed sub-second |
| EP0014 closed | `scripts/status.py backlog --type epic` (or grep EP0014 status) | GREEN - EP0014 Done |
| Open-bug count 0 | `scripts/status.py backlog --type bug` | **RED (2026-07-09)** - BG0067/0068/0069/0070 at `Fixed`, not yet `Closed`; US0112 closes them |
| Reconcile drift 0 | `scripts/reconcile.py detect` | GREEN - drift 0 |
| Full suites green | script + tools unittest discover | GREEN - 1449 + 105 |

## Verdict

**NOT YET GREEN (2026-07-09).** One gate is red: the open-bug count is not 0 because four bugs
sit at `Fixed` pending closure (US0112 in this sprint closes them). Once US0112 lands and the bug
count reaches 0, every gate above is green and the rc tag decision is a clean checklist read. The
operator cuts `v4.0.0-rc.1` and pushes at that point - not before.
