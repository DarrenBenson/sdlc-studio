# BG1722: `conformance.adopt_after` takes a schema v3 cutoff on a schema v2 project, so the conformance lane exempts every sequential unit

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py, changelog.d/BG1722.md
> **Evidence:** Found by the run twenty-three EFCI2 builder and marked pre-existing by the qa reviewer of BG0959: conformance.py:617 and validate.py:738 pass `allow_ulid` with no schema check.
> **Created:** 2026-11-23
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-23T08:33:31Z

## Summary

BG0959 (run twenty-three) makes the engagement floor refuse a v3 `adopt_after` cutoff such as BG-01KX95QP before the project is on schema v3, because on a v2 project such a cutoff sits above every sequential id and exempts them all, including ones not yet minted. `conformance.adopt_after` reads the same cutoff through `parse_cutoff` with `allow_ulid` (conformance.py around line 617, validate.py around line 738) and still accepts it on a v2 project, so the conformance lane silently stops checking every unit.

## Steps to Reproduce

1. In a schema v2 project, set `conformance.adopt_after` to BG-01KX95QP in sdlc-studio/.config.yaml. 2. Run conformance.py over a sequential unit that breaks a conformance rule. 3. Observe it is exempt and the run is clean, where the engagement floor refuses the same cutoff.

## Proposed Fix

Refuse a v3 cutoff in `conformance.adopt_after` before schema v3, as the engagement floor now does, with the same remedy text, in conformance.py and validate.py.

## Acceptance Criteria

- [ ] **AC1** Given a schema v2 project whose `conformance.adopt_after` is a v3 id, when conformance.py and validate.py read it, then each refuses it with the engagement floor's remedy and exits non-zero. Fails on: the lane running with every sequential unit exempt.
- [ ] **AC2** Given a schema v3 project with the same cutoff, when they read it, then it is honoured as today. Fails on: a v3 project refused.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-23 | sdlc-studio | Filed |
