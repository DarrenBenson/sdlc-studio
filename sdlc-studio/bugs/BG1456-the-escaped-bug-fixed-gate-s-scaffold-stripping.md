# BG1456: The escaped-bug Fixed gate's scaffold stripping is untested and matches the scaffold by exact string, and test_file_finding's selector reader test fails outside a git checkout

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_escape_gate_scaffold.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, changelog.d/BG1456.md, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** Run thirteen (RUN-01M7EYR3) review of US1157, qa-seat-US1157-r1, verdict sdlc-studio/reviews/verdicts/US1157/4128762ea8a7-ba15f7f2.txt
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run thirteen orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T08:02:04Z

## Summary

Run thirteen's US1157 review (APPROVE, non-blocking): the Fixed gate strips template slots, HTML comments and blockquoted prompt lines (transition.py:150-151) with no test (mutant M11 survives); it finds the scaffold by exact string (transition.py:149), so a scaffold re-wrapped across two lines counts as a written cause; and `test_file_finding.py`::VerifySelectorWriteGuardTests::`test_one_reader_answers_which_file_a_selector_targets` fails in a clean archive of the tree (no .git) though it passes in a checkout and at the push gate.

## Steps to Reproduce

Delete the re.sub at transition.py:150-151 and run `test_bug_escape_fields.py`: green. Re-wrap the scaffold across two lines and run `transition.py set --id BG0001 --status Fixed --dry-run`: it would set Fixed. Run the `file_finding` selector test from `git archive` output: it fails.

## Proposed Fix

Pin the stripping; match the scaffold after normalising whitespace; make the selector test build its own git fixture or skip with a reason outside a checkout.

## Acceptance Criteria

- [ ] **AC1** Given an escaped bug whose root cause holds only the template scaffold, wrapped or not, when it moves to Fixed, then it is refused, and deleting the stripping fails a test. Fails on: a re-wrapped scaffold accepted.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_escape_gate_scaffold.py::EscapeGateScaffoldTests
- [ ] **AC2** Given a tree with no .git, when the selector reader test runs, then it passes or skips with its reason. Fails on: a bare failure.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run thirteen orchestrator) | Filed |
