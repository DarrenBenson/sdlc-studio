# CR-0496: A project-config decision is invisible to the forward-port check, so 'in sync' reads as 'everything is mirrored' when the reasoning stayed behind

> **Status:** In Progress
> **Decomposed-into:** EP0219
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** Claude Opus 5; human; v1
> **Affects:** tools/forward-port.sh, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py, tools/tests/test_forward_port.py
> **Priority:** Medium
> **Type:** enhancement
> **Size:** M

## Summary

`tools/forward-port.sh --check` mirrors the skill tree and reports `in sync`. It does not cover `sdlc-studio/.config.yaml`, which is project state by design. That design is right - another project's conformance cutoff, gate budget and capacity are its own - but two consequences of it are currently unmanaged.

First, the check's verdict overstates itself. It says `in sync` without naming what it did not compare, so an operator reading it concludes the machine is uniformly current. Tonight's `conformance.adopt_after` restore to 82 (D0076) is in force in this repo alone; every other project on this machine loads the same skill with its own threshold and none of the reasoning.

Second, and the sharper one: a grandfathering threshold is raised with a RESTORE CONDITION written in a YAML comment. That condition is prose no tool reads. The 82 -> 310 raise of 2026-07-24 outlived its own stated expiry by four days for exactly this reason, and the wording that let it (an APPROVE, rather than an APPROVE covering WHICH UNITS) was only caught by re-reading the comment by hand. A condition nothing checks is a note, not a control.

## Impact

A threshold raised as a temporary exemption stays raised silently. The 2026-07-24 raise exempted 228 units for four days past its expiry; the 2026-07-28 raise was caught within the hour only because the operator happened to challenge it. The check's own `in sync` line is the second half of the same problem - a green verdict whose scope is not stated is read as covering everything.

## Acceptance Criteria

- [ ] The forward-port check names what it does not compare. `--check` reports the scope of its verdict, naming project-state files (`sdlc-studio/.config.yaml`, `.local/`) as deliberately outside the mirror, so `in sync` cannot be read as `everything is current`.
- [ ] A grandfathering threshold carries a machine-readable restore condition. A raise to `conformance.adopt_after`, `provenance.adopt_after` or `engagement_floor.adopt_after` records the condition alongside the number in a form a tool can evaluate - which units the exemption exists for, and what discharges it.
- [ ] A fired restore condition is reported. When the condition holds, a gate lane or a status advisory says the exemption is discharged and names the number it should return to; an exemption whose condition has fired is a finding, not a silence.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Related: CR0497 applies the same rule at the ADOPTION moment. This one is about an exemption granted mid-life by an operator who knows why; that one is about the exemptions v5 grants a project automatically on the day it upgrades, when nobody has written a reason down at all. Same defect, two moments. |
