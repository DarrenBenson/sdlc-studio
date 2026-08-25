# BG0612: Three limbs that survived the closure of BG0599 and BG0602: an edit-verb gap, an unpinned checklist roster and an import-time blind spot

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** Both parent filings were re-verified against source by an independent goal review on 2026-08-25 before any code was written, and closed with the source lines that settle them recorded on each artefact. This unit carries only the limbs that survived that verification.
> **Created:** 2026-08-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0599 and BG0602 were closed on 2026-08-25 because their stated causes do not reproduce at HEAD - derive already reports every fault in one invocation, and the close checklist is an explicit tuple rather than a name-prefix scan. Three narrower defects inside those filings do stand, and are carried here rather than lost with the artefacts that named them.

## Steps to Reproduce

Edit verbs: `verify_ac.py`'s `_EDIT_VERBS` holds 61 verbs and omits `restore` and `keep`, so a mutant phrased as 'restore the base constant' is refused for carrying no edit verb while a synonym passes - observed repeatedly while authoring test plans on RUN-01M0JD1W. Roster: `sprint_report.py`'s `CHECKLIST` tuple is asserted by no test that pins its names or its length, so a check removed from it is a silent shrink. Import blind spot: `_resolve_item` resolves a checklist entry through `globals().get(...)` at call time, so an entry naming a function nobody wrote is discovered when the close runs rather than when the module loads.

## Proposed Fix

Add the two missing verbs and a test that fails on their absence. Pin the CHECKLIST roster by exact names and count. Resolve every registered check at import and refuse there, so a registered-but-undefined entry cannot reach a close.

## Acceptance Criteria

- [ ] **AC1** Given a mutant cell phrased with `restore` or `keep` as its edit verb, when `testplan derive` runs, then it is accepted - and given a cell with no edit verb at all, it is still refused, so the vocabulary is widened rather than disabled
- [ ] **AC2** Given the close checklist roster, when its test runs, then it asserts the exact names and the exact count, so removing an entry fails rather than shrinking the report
- [ ] **AC3** Given a checklist entry naming a resolver nobody defined, when `sprint_report` is imported, then it refuses there - not when the close runs, which is the point at which a missing check is least recoverable
- [ ] **AC4** Given a roster with every entry defined, when the module is imported, then it loads normally - the paired control, so the import check is shown to discriminate

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-25 | sdlc-studio | Filed |
