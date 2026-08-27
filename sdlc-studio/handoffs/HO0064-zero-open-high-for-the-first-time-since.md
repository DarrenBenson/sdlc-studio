# HO-0064: Zero open High for the first time since v5.0.1, and every unit rejected first

> **Date:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Run:** RUN-01M0YXN3 (started 2026-08-26T11:38:21Z)
> **Outcome:** goal-reached
> **Goal:** done
> **Batch source:** run-state.json

## Where to pick up

**The release bar is MET** - `known_issues.py --bar` exits 0, and it is measured on a checker
BG0621 hardened first in this very run, so its green is evidence rather than an artefact of a
case-sensitive match, a single literal status, or a heading pattern that skipped 21 files.

Every unit is terminal and signed off. Before planning the next batch, read two things:

- **BG0625** - an empty brief on both rows lets a cross-seat APPROVE retire a REJECT, which re-arms
  the whole of BG0607 for any project that stands the `--brief` requirement down. It is latent here
  only because every one of 854 rows carries a brief.
- **The nineteen waivers** in `sdlc-studio/decisions.md`. BG0607's roll-up surfaces nineteen units
  carrying a rejection no seat ever answered, and they are set aside by recorded judgement rather
  than repaired. What is waived is the historical gap, not the rule: every unit reviewed after
  2026-08-27 is held to it in full.

Nine bugs and four CRs were filed from this run's five reviews. None is at a barred severity.

## Appetite

- **Declared:** wall-clock 5760 min, units 64 unit(s)
- **Spent:** 1283.3 min, 4 unit(s) terminal
- **Delivered:** 4 unit(s)
- **Token forecast:** ~2,520,746 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (4)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0621](../../sdlc-studio/bugs/BG0621-the-release-bar-can-report-met-while-a.md) | bug | Fixed | 9/9 AC(s) verified; critic REJECT (engineering seat (subagent, wave 1)) |
| [BG0615](../../sdlc-studio/bugs/BG0615-an-abandoned-guided-onboarding-marker-outranks-the-whole.md) | bug | Fixed | 5/5 AC(s) verified; critic REJECT (qa seat (subagent, close)) |
| [BG0618](../../sdlc-studio/bugs/BG0618-a-repair-s-evidence-is-split-on-a.md) | bug | Fixed | 8/8 AC(s) verified; critic REJECT (engineering seat (subagent, wave 2)) |
| [BG0607](../../sdlc-studio/bugs/BG0607-a-unit-s-verdict-is-the-last-row.md) | bug | Fixed | 7/7 AC(s) verified; critic REJECT (engineering seat (subagent, wave 3)) |

## Remaining (0)

_Nothing remains: every unit in the batch reached a terminal status._

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Generated at the run close (`handoff generate`) |
