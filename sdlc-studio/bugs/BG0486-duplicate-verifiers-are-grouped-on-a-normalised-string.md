# BG0486: duplicate verifiers are grouped on a normalised string, so two ACs running the same command can read as distinct

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Carved out of BG0433, whose other two halves are delivered. The duplicate-verifier ratchet groups on a NORMALISED STRING rather than on the resolved argv, so two criteria that run the identical command can be grouped apart when their spelling differs - a different runner prefix, a reordered flag, an extra `-q`. The ratchet then reports no duplicate where one exists, which is the failure the whole lane is for: two ACs sharing a selector cannot both discriminate, and a regression in either fails both while neither says which.

Not delivered alongside the other halves deliberately. Regrouping reshapes the very baseline BG0433 just brought under the shrink guard, and doing both in one step would leave neither measurable - the new grouping's yield could not be told from the reader fix's.

## Steps to Reproduce

1. Author two ACs whose Verify lines resolve to the same command with different spelling (e.g. `pytest x.py::T::t` and `python3 -m pytest x.py::T::t`).
2. Run the ratchet; the pair is not reported as a duplicate group.

## Proposed Fix

Group on the RESOLVED argv the runner would execute, not on the written string. Re-baseline afterwards and record the before/after group count, so the regrouping's effect is a measured number rather than an assertion.

## Acceptance Criteria

- [ ] The behaviour described is corrected: Carved out of BG0433, whose other two halves are delivered.
- [ ] The proposed fix lands, pinned by a test: Group on the RESOLVED argv the runner would execute, not on the written string.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | Claude Opus 5 | Filed |
