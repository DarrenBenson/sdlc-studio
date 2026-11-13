# BG1420: Run eleven's lanes turn the full suite red in five tests the per-commit runs never selected

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_workers.py, tools/tests/test_dependency_advisories.py, tools/tests/test_lean_release_notes_v63.py, tools/tests/test_lean_release_notes.py, changelog.d/BG1420.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** RUN-01M78TKD, 2026-11-13: push of b7ead759 refused by the devserver1 boundary gate (5 red of 8869)
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:39:36Z

## Summary

The push gate at b7ead759 ran the full suite and refused it with 5 red: a bare artefact read in `verify_ac`'s new skip-mark scanner (lines 441 and 460); an interrupt no longer cancelling the verify lane's queued stories after the new signal handler (6 started, not 3); `test_dependency_advisories` still pinning markdownlint-cli ^0.49.0 after the upgrade to ^0.50.0; the 6.3 release-notes test's premise that BG1190 is Open; and the frozen-notes test that files a finding in a copy and finds the tools suite red. Each lane's commit ran only the modules its change selected.

## Steps to Reproduce

Run tools/run-suite.sh all at b7ead759, or push: the gate host reports these five tests red.

## Proposed Fix

Route the scanner's reads through `sdlc_md.read_text_safe`; restore the interrupt's cancellation of queued stories while keeping the signal relay; re-point the two tests whose premises the run changed (the advisory pin and BG1190's status), each only as far as the new state requires; find and fix why the frozen-notes test's tools suite turns red after a filing.

## Acceptance Criteria

- [ ] **AC1** Given main after the fix, when the five named tests run, then each passes: BareArtefactReadSweepTests::`test_no_bare_artefact_body_reads_in_scanners`, PoolEdgeTests::`test_an_interrupt_cancels_the_stories_still_queued` (only the three running stories ever start), LockfileTests::`test_package_json_was_not_widened_to_clear_the_advisory`, ReleaseNotesTests::`test_every_changed_behaviour_names_what_to_do` and FrozenNotesTests::`test_filing_a_finding_reddens_no_test.` Fails on: any of the five red, or a test deleted or skipped to make it pass.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repo_hygiene.py::BareArtefactReadSweepTests::test_no_bare_artefact_body_reads_in_scanners .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_workers.py::PoolEdgeTests::test_an_interrupt_cancels_the_stories_still_queued tools/tests/test_dependency_advisories.py::LockfileTests::test_package_json_was_not_widened_to_clear_the_advisory tools/tests/test_lean_release_notes_v63.py::ReleaseNotesTests::test_every_changed_behaviour_names_what_to_do tools/tests/test_lean_release_notes.py::FrozenNotesTests::test_filing_a_finding_reddens_no_test

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
