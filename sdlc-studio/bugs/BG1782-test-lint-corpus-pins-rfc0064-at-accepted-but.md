# BG1782: `test_lint_corpus` pins RFC0064 at Accepted, but its status is derived from its children and reconcile moved it to Delivered

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_lint_corpus.py, changelog.d/BG1782.md
> **Evidence:** Run twenty-eight's push of main (2026-11-27, 23:30Z) was refused by the pre-push full suite (sdlc-studio/.local/boundary-suite-last.log): 2 red of 10874.
> **Created:** 2026-11-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M8B7DJ - raised during the run, 2026-11-28T00:13:57Z

## Summary

CorpusLaneRunsOnThisRepo::`test_no_accepted_rfc_here_has_a_pending_decision` asserts `> **Status:** Accepted` for RFC0063 and RFC0064 as its positive control. RFC0064's status is derived from its children (its Forced-override line says so); once CR0695 and CR0696 were Done, `reconcile apply` in run twenty-eight's paperwork commit 105c02fcb moved it to Delivered, which is right. The test is now red on main, so the push gate refuses every push. The control's point, that the rule reads these RFCs' Decision blocks, still holds for a Delivered RFC.

## Steps to Reproduce

1. On main, run `python3 -m pytest tools/tests/test_lint_corpus.py::CorpusLaneRunsOnThisRepo::test_no_accepted_rfc_here_has_a_pending_decision`.
2. It fails: `'> **Status:** Accepted' not found` in RFC0064, whose status reads Delivered.

## Proposed Fix

Let the positive control take an RFC at Accepted or a later status the RFC lifecycle allows (Delivered), keep checking every Decision field, and show that `lint_corpus.accepted_rfc_decision_findings` still reads a Delivered RFC's Decision block (or, if it reads only Accepted ones, pick the control from the RFCs it does read).

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: CorpusLaneRunsOnThisRepo::`test_no_accepted_rfc_here_has_a_pending_decision` asserts `> **Status:** Accepted` for RFC0063 and RFC0064 as its positive control.
  - **Verify:** pytest tools/tests/test_lint_corpus.py::CorpusLaneRunsOnThisRepo::test_no_accepted_rfc_here_has_a_pending_decision
  - **Verified:** yes (2026-11-28)
- [ ] **AC2** The proposed fix lands, pinned by a test: Let the positive control take an RFC at Accepted or a later status the RFC lifecycle allows (Delivered), keep checking every Decision field, and show that...
  - **Verify:** pytest tools/tests/test_lint_corpus.py::CorpusLaneRunsOnThisRepo::test_no_accepted_rfc_here_has_a_pending_decision
  - **Verified:** yes (2026-11-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-28 | sdlc-studio | Filed |
