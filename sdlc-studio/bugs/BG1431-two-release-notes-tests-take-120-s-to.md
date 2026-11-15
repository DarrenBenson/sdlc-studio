# BG1431: Two release-notes tests take 120 s to over 300 s under load, past verify_ac's default per-verifier timeout, so BG1420's and BG1425's recorded runs fail on time unless given --timeout

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/tests/test_lean_release_notes.py, tools/tests/test_lean_release_notes_v63.py, changelog.d/BGXXXX.md
> **Evidence:** Run twelve (RUN-01M7E52T) review of BG1425 and BG1420's rejoinder ([pre-existing]); the orchestrator accepted both with --timeout 600
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T00:57:28Z

## Summary

BG1420 AC1 (and BG1425 AC2, which carries it) names five tests; under load `verify_ac run` with its default 120 s per-verifier timeout (`verify_ac.py`:5263) reported 'FAIL AC2 | timeout' at 133 s and 121 s, and FrozenNotesTests::`test_filing_a_finding_reddens_no_test` alone took 322 s. With `--timeout 590` on an idle host the run passes in 141 s. The test is unchanged since 0f55861a.

## Steps to Reproduce

Run `verify_ac.py run --id BG1425` on a loaded host with the default timeout: AC2 fails on time.

## Proposed Fix

Make the frozen-notes test build a minimal fixture instead of filing into a full tree copy, so it runs well inside the default timeout.

## Acceptance Criteria

- [ ] **AC1** Given a loaded host, when FrozenNotesTests::`test_filing_a_finding_reddens_no_test` runs, then it finishes in under 60 s. Fails on: a run over the default per-verifier timeout.
  - **Verify:** pytest tools/tests/test_lean_release_notes.py::FrozenNotesTests::test_filing_a_finding_reddens_no_test

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
