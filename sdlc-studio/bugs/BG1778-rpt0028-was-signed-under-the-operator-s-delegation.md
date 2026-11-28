# BG1778: RPT0028 was signed under the operator's delegation, and nothing discloses it

> **Status:** Fixed
> **Severity:** Low
> **Points:** 2
> **Affects:** sdlc-studio/reports/RPT0028-sprint-report-run-01m7061x.md, sdlc-studio/reports/RPT0028.json, sdlc-studio/reports/evidence-pack-6.4.0.md, docs/evidence.md, tools/tests/test_lean_delegated_reports_disclosed.py, changelog.d/BG1778.md
> **Created:** 2026-11-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M8B7DJ - raised during the run, 2026-11-27T19:33:02Z

## Summary

RPT0028 (run nine, RUN-01M7061X) was signed by the delegate: its seal commit 45db061c3 quotes the operator's "I authorise you to sign for me". But no decision, bug or CR records that, so the report, its 15 lines in the 6.4.0 evidence pack and its row on docs/evidence.md read as the operator's own signature. US1295 disclosed RPT0029 to RPT0034 under D0640 and took RPT0028 as signed in person. Its test, `tools/tests/test_lean_delegated_reports_disclosed.py`, says so at line 64 (a comment) and line 231 (an assertion message), and its AC2 asserts it. Found by US1295's qa review (verdict 6fd9c75adad4-0fb7a991). A smaller item from the same review: RPT0031 names D0475 while its seal commit names D0479. Both decisions cover run twelve, but f946c5460's commit says the decisions were traced from the seal commits.

## Steps to Reproduce

1. git show 45db061c3 and read the quoted authorisation.
2. Read sdlc-studio/reports/RPT0028-sprint-report-run-01m7061x.md: it carries no delegation disclosure.
3. Read the RUN-01M7061X row of docs/evidence.md and RPT0028's lines in sdlc-studio/reports/evidence-pack-6.4.0.md.

## Proposed Fix

Record the delegation behind RPT0028 as a decision row (as D0640 did for RPT0029 to RPT0034). Add the disclosure line to RPT0028 and its JSON, and rebuild the 6.4.0 pack. Correct the evidence.md row, and widen the test, including its comment and message, to cover RPT0028.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: RPT0028 (run nine, RUN-01M7061X) was signed by the delegate: its seal commit 45db061c3 quotes the operator's "I authorise you to sign for me".
  - **Verify:** pytest tools/tests/test_lean_delegated_reports_disclosed.py::DelegatedReportsDisclosedTests::test_each_delegated_report_names_its_decision_and_checks_valid
  - **Verified:** yes (2026-11-28)
- [ ] **AC2** The proposed fix lands, pinned by a test: Record the delegation behind RPT0028 as a decision row (as D0640 did for RPT0029 to RPT0034).
  - **Verify:** pytest tools/tests/test_lean_delegated_reports_disclosed.py::DelegatedReportsDisclosedTests::test_the_evidence_pack_and_page_name_the_delegated_signatures
  - **Verified:** yes (2026-11-28)

## Impact

A reader of the 6.4.0 evidence takes one delegated signature as the operator's own, which is the exact misreading D0640 set out to remove.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-27 | sdlc-studio | Filed |
