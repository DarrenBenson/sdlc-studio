# BG1297: The 6.3.0 release-notes test checks the CLI against expectations typed into the test, not against the notes, so a notes sentence naming a wrong flag, trailer or verb still passes

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/tests/test_lean_release_notes_v63.py
> **Evidence:** US1136 round-2 review (qa-seat-US1136-r1), notes mutants
> **Created:** 2026-11-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-08T18:18:03Z

## Summary

From US1136's round-1 and round-2 reviews (qa-seat-US1136-r1, non-blocking). `commit_msg_claims` and `agent_definition_claims` (tools/tests/`test_lean_release_notes_v63.py`:729-809) run the CLI and compare it with expectations written in the test, and only the `--force` file list is read from the notes. Each of these notes mutants, applied alone, leaves the module at 4 passed: an invented `--no-refs` flag in the Refs Instead, `Closes:` for `Mentions:` among the trailers the flag writes, `lane approve` for `lane accept`, and BG1290's "refuses to record a verdict" changed to "records the verdict". All six of round 1's untested-claim mutants also survive (`--force` to `--overwrite`, `cost --anatomy` to `--breakdown`, `lane run --harness` to `--cli`, `gemini` for `copilot` and `opencode`, five harnesses to six, `CURSOR_API_KEY` alone). The same shape will recur in each release's notes test.

## Steps to Reproduce

Apply any one of the mutants above to docs/release-notes-v6.3.0.md and run `python3 -m pytest -q tools/tests/test_lean_release_notes_v63.py`: 4 passed.

## Proposed Fix

Read each claimed flag, verb, trailer and harness name from the notes and check it against the shipped CLI (`--help`, the trailer writer, the HARNESSES tuple), so a wrong name in the notes fails. Make that a reusable helper the next release's notes test calls.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: From US1136's round-1 and round-2 reviews (qa-seat-US1136-r1, non-blocking).
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Apply any one of the mutants above to docs/release-notes-v6.3.0.md and run `python3 -m pytest -q tools/tests/test_lean_release_notes_v63.py`: 4 passed.
- [ ] **AC3** The proposed fix lands, pinned by a test: Read each claimed flag, verb, trailer and harness name from the notes and check it against the shipped CLI (`--help`, the trailer writer, the HARNESSES tuple)...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Filed |
