# BG1161: A clean-checkout gate.py run judges conformance over the whole workspace and reads OVER the standard budget every time

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate_budget.py, changelog.d/BG1161.md, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** BG1065 builder report, 2026-11-01, outside-the-unit item 1: clean-tree run 798.9s, conformance 768.3s.
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T06:34:26Z

## Summary

Found by BG1065's builder (2026-11-01). On a clean tree, `changed_story_ids` returns None, so conformance judges all 1100+ units. A clean-tree `gate.py --root .` took 798.9s, 768.3s of it conformance, at load 10-14, against a 45s budget that BG1065 now records beside a measured staged-change run (39.8s). CI runs the clean-checkout form, so its cost line reads OVER on every run and carries no signal: the defect BG1065 fixed for commits, now confined to CI.

## Steps to Reproduce

1. On a clean checkout run `python3 .claude/skills/sdlc-studio/scripts/gate.py --root .`.
2. Read the cost line: OVER, with conformance dominant.

## Proposed Fix

Give the clean-checkout (CI) run its own measured budget, or scope its conformance to the pushed range as the push boundary does.

## Acceptance Criteria

- [ ] **AC1** A clean-checkout gate run is judged against a budget recorded beside a measured clean-checkout run, or its conformance is scoped so the standard budget applies.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_budget.py

## Impact

CI's gate cost line is permanently OVER, so a real ratchet would not be noticed there.

## Notes

- From BG1065's review (2026-11-01): `gate.py --release` with no boundary runs a different lane set (whole-workspace conformance and validate plus the verify lane) yet is compared with and recorded as the standard baseline (it printed '88% faster than the 0.6s baseline' and overwrote gate-cost.json on a fixture), from the same `if record and not scoped` branch BG1065 fixed for boundaries. Fold it into this unit.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
