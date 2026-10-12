# BG1022: A stale TSD still says the batch does not deliver Unit Testing

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_plan_stale_tsd_gaps.py, changelog.d/BG1022.md
> **Evidence:** Field report, 2026-10-09, both plans of RUN-01M4FSND on sdlc-studio-lens. The plan printed that the TSD is stale because the code outside sdlc-studio/ changed on 2026-10-07 and the TSD was last revised on 2026-07-13. The next lines said the batch touches no TSD risk area, then 'coverage the TSD demands that this batch does NOT deliver: Integration Testing, Unit Testing'. The stories in that batch declare new test files, including backend/tests/test_ingest.py and frontend/src/pages/Reports.test.tsx. The July TSD names older test files, so the new ones do not match.
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Grok 4.7; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-09T16:38:36Z

## Summary

`tsd_levels` collects only backtick paths that end in py, sh, md, json or yaml. A batch touches a level only when one of those exact paths is a substring of an Affects entry. Every other level that named at least one such path is a gap, and the plan prints that the batch does not deliver that level. The staleness warning is printed first, and the gap line is printed after it in the same voice as a current obligation. A new test file the stale document could not have named therefore reads as a failure to deliver unit testing. The reader who is told the code has moved past the document is then told the batch failed a demand taken from that document.

## Steps to Reproduce

1. On a project whose tsd.md Unit Testing section names one existing test file, and whose code is newer than the TSD, plan a story whose Affects is a different new test file. 2. The plan says the TSD is stale. 3. It also says the batch does not deliver Unit Testing.

## Proposed Fix

When `tsd_staleness` says the document is stale, do not print those gaps as coverage the batch failed to deliver. Say the gap list was not read because the TSD is stale. A current TSD keeps the existing gap line.

## Acceptance Criteria

- [ ] **AC1** A plan whose TSD is stale says so and does not print any test level as coverage the batch does not deliver; a plan with a current TSD keeps the gap line
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_stale_tsd_gaps.py::StaleTsdGapTests::test_a_stale_tsd_prints_no_delivery_gaps

## Triage

- Reproduced in this repository on 2026-10-09: the EP0274 plan preview printed `the TSD is STALE` and then `coverage the TSD demands that this batch does NOT deliver: Coverage Targets, Eval Scenarios, Integration Testing ...`. Pre-existing.
- Severity Medium stands: a stale document's gaps are printed as the batch's failures. Fragment renamed to the unit id.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | Grok 4.7 | Filed |
| 2026-10-12 | Claude Opus 5.5 (triage) | Triaged: confirmed on current code; changelog fragment named for the unit; Verify on a new test module (BG0980) |
