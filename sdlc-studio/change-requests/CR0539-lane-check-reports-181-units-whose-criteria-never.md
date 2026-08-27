# CR-0539: lane-check reports 181 units whose criteria never enter a shipped entry point

> **Status:** In Progress
> **Decomposed-into:** EP0235
> **Priority:** Medium
> **Type:** process
> **Size:** L
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Date:** 2026-08-08
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio-authoring-session; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`verify_ac.py lane-check` reports 181 units across the corpus whose acceptance criteria are verified only by library tests, though the unit changes a command. It runs advisory and prints during every commit, so the number is visible and acted on by nobody. Repairing the eight units of RUN-01KZF9AF by hand found two real defects a library test could not see: `docgen.py references` and `surface` called their renderers with no argument, so `--root` selected which file was written while the content came from the real installed tree; and `nesting_depth` had zero non-test callers, the same shape as BG0541. That is a two-defect yield from eight units, which argues the other 173 are worth working through rather than living as a permanent advisory.

## Impact

The rule AGENTS.md states - exercise every claim through the shipped entry point before asking for review - has a checker that names 181 violations and blocks none of them. A report at that volume reads as background noise, so the gate LL0027 asks for does not exist in practice. The two defects found while clearing eight units were both invisible to a green library suite.

## Acceptance Criteria

- [ ] lane-check records the corpus count as a baseline and refuses an INCREASE, so a new unit cannot add a criterion that never enters its own command while 181 existing ones stay reported.
- [ ] The baseline falls when a unit is repaired and never rises silently: lowering it is automatic, raising it needs a recorded decision.
- [ ] A unit under construction sees its OWN lane-check line at delivery, not only the corpus total - a report of 181 is background noise, a report of one is a finding.

## Recommendation

Ratchet rather than block: record 181 as the baseline, refuse an INCREASE, and let the number fall as units are repaired. A blocking check over 181 existing violations gets switched off on day one; a ratchet costs nothing today and cannot regress. Pair it with a per-unit report at delivery so a unit under construction sees its own line rather than the corpus's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-08 | sdlc-studio-authoring-session | Raised |
