# BG1442: evidence_pack.py reaches into critic's private `_id` normaliser, so test_critic's one-independence-authority guard is red on main

> **Status:** Fixed
> **Severity:** High
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/evidence_pack.py, .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_build.py, .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_accountable.py, changelog.d/BG1442.md
> **Evidence:** Run twelve (RUN-01M7E52T) US1153/US1154 lane land refused on test_critic.py:1340 (regression from BG1439 and US1155)
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T04:26:02Z

## Summary

BG1439's `unit_authors` and US1155's `_independent_reviews` call `critic._id(...)` (scripts/`evidence_pack.py`:127 and :241). `test_critic.py`::OneIndependenceAuthorityTests::`test_NO_module_hand_rolls_the_independence_comparison` refuses any module that rebuilds the independence comparison from critic's private parts, so main has been red since BG1439 landed; the lands' selected test runs did not include `test_critic.py`, and the US1153/US1154 land, which touches critic.py, found it.

## Steps to Reproduce

Run pytest .claude/skills/sdlc-studio/scripts/tests/`test_critic.py`::OneIndependenceAuthorityTests on main: it names `evidence_pack.py`:127 and :241.

## Proposed Fix

Use critic's public identity function (the one `round_refusal` uses, `critic.same_identity`, or a public normaliser) for the author list and the per-reviewer dedupe, keeping every evidence-pack test green.

## Acceptance Criteria

- [ ] **AC1** Given main after the fix, when `test_critic`'s one-independence-authority guard runs, then it names no line of `evidence_pack.py`, and every evidence-pack test still passes. Fails on: any `critic._` private call left in `evidence_pack.py.`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::OneIndependenceAuthorityTests::test_NO_module_hand_rolls_the_independence_comparison .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_build.py .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_accountable.py
  - **Verified:** yes (2026-11-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
