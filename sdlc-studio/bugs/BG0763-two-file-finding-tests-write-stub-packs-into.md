# BG0763: Two file_finding tests write stub packs into the shipped audit-profiles folder, so parallel runs race

> **Status:** Fixed
> **Verification depth:** functional (the race reproduced at the base under -n 8 and eight patched runs were green; the shipped packs folder stayed byte-identical over five runs; two mutants killed)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_audit_pack_isolation.py, changelog.d/BG0763.md
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`test_file_finding.py`'s AuditAttributionUnheldInvariantsTests write zz-review-stub.md and zz-review-dupe.md into the real templates/audit-profiles/ directory. Under pytest-xdist a sibling test's duplicate pack makes `LIVE_LENS` ambiguous, so `test_a_stub_pack_elsewhere_does_not_break_an_unrelated_filing` fails at random. It refused BG0762's commit on 2026-09-25 and passes alone every time.

## Steps to Reproduce

Run the commit hook's selected suites under load with `test_file_finding.py` selected; about one run in several fails `test_a_stub_pack_elsewhere_does_not_break_an_unrelated_filing` on an ambiguous lens. Alone it passes.

## Proposed Fix

Point `file_finding`'s pack lookup at a per-test temporary copy of the packs folder (a parameter or environment override the tests set), so no test writes into the shipped templates; delete nothing the tests prove.

## Acceptance Criteria

- [ ] **AC1** Given the audit-attribution tests that need a stub or duplicate pack, when they run, then they write it into a per-test temporary copy of the packs folder and nothing is written under the shipped `templates/audit-profiles/`; a fix that only reorders or serialises the tests, leaving the writes in the shipped folder, fails it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_audit_pack_isolation.py::AuditPackIsolationTests::test_no_test_writes_into_the_shipped_packs_folder
  - **Verified:** yes (2026-09-25)
- [ ] **AC2** Given the stub and duplicate pack tests run concurrently under pytest-xdist, then each still proves its own case (a stub pack elsewhere does not break an unrelated filing; an ambiguous lens is refused) with no cross-test interference; a lookup that ignores the override and reads the shipped folder fails it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_audit_pack_isolation.py::AuditPackIsolationTests::test_the_pack_lookup_reads_the_override_not_the_shipped_folder
  - **Verified:** yes (2026-09-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
| 2026-09-25 | Claude Opus 5.5 | Criteria authored with Verify lines; joined the Sprint 4 batch after the race refused three commits |
