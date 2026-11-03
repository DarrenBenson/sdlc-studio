# BG1185: BG1167's rule reads a light APPROVE's scope from git history, so three narrow orderings still count a unit whose own Affects widened as covered

> **Status:** Open
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py, changelog.d/BG1167.md, changelog.d/BG1185.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** BG1167 round-2 verdict, 2026-11-03 (critic-verdicts.md), and its probes in scratchpad/run5/bg1167qa/r2/.
> **Created:** 2026-11-03
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-03T01:28:42Z

## Summary

BG1167 round 2's review (qa-seat-BG1167-r1, APPROVE, 2026-11-03) found three non-blocking fail-open cases against BG1167 AC3, each probed through the shipped CLI. (1) Two light APPROVE rows on one brief fingerprint more than two days apart, the later committed after the unit's own widening: `--since` is cut from the newer row's date (critic.py:3330), so the older commit drops out of the pickaxe and the later commit's parent, which carries the widened Affects, is read. A 10-day gap gives conformant=True. This makes changelog.d/BG1167.md:15 ('the older row's commit decides') false beyond the window. (2) A widening committed on its own between the record and the ledger commit: the recording commit's parent already carries it (critic.py:3340). (3) A full repository with `log.showRoot=false`, a first row in the root commit and a later row after the widening: the pickaxe skips the root commit (critic.py:3327). The pre-BG1167 rule refused all three.

## Steps to Reproduce

Run the reviewer's probes in scratchpad/run5/bg1167qa/r2/ (p2.py, final.py) against main at or after 1696cce8.

## Proposed Fix

Record the unit's declared Affects in the delivery row at `critic.py record` time, and compare today's Affects with that, which makes all three orderings moot. At minimum, floor `--since` at the oldest row carrying the fingerprint and pass `--root` to the pickaxe. Correct changelog.d/BG1167.md:15 either way.

## Acceptance Criteria

- [ ] **AC1** Each of the three orderings leaves the widened unit non-conformant, with a dated-commit test per ordering, and changelog.d/BG1167.md states only what holds.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::TierCoverageTests

## Impact

In each ordering, a unit whose own scope grew after a light review is counted as reviewed deeply enough.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-03 | claude | Filed |
