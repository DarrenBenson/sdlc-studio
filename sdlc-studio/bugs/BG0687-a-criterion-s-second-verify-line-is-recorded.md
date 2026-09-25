# BG0687: A criterion's second Verify line is recorded but never run, so a both-states requirement cannot be enforced by its selectors

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_verify_every_line.py, changelog.d/BG0687.md
> **Evidence:** BG0667 round-5 plan repair, RUN-01M2JA6J 2026-09-15.
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`verify_ac` reads the first Verify line under a criterion and records any later one without running it. A criterion that must hold in two environments (BG0667 AC5: green with and without `SDLC_STUDIO_BOUNDARY_SUITE`=1) can name both commands, and only the first is ever executed, so the second state is enforced by nobody.

## Steps to Reproduce

1. Give a criterion two Verify lines, the second failing.
2. `verify_ac.py` run --id <unit> reports the criterion pass.

## Proposed Fix

Run every Verify line under a criterion and pass it only when all pass; or refuse a second line at lint time with the reason named.

## Acceptance Criteria

- [ ] **AC1** Given a criterion carrying two `Verify:` lines, the first passing and the second failing, when `verify_ac.py run --id` runs, then the criterion is reported failed and the output names the failing line. Fails on: HEAD, which runs only the first line and reports `pass=1` (reproduced in a fixture: `shell test -d /` then `shell test -d /nonexistent`)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_verify_every_line.py::VerifyEveryLineTests::test_a_failing_second_line_fails_the_criterion
- [ ] **AC2** Given a criterion whose first `Verify:` line fails and second passes, then the criterion is reported failed. Fails on: running only the last line
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_verify_every_line.py::VerifyEveryLineTests::test_a_failing_first_line_fails_the_criterion
- [ ] **AC3** Given a criterion whose two `Verify:` lines both pass, then it is reported passed and stamped once. Fails on: refusing every second Verify line, which turns a both-environments criterion (BG0667 AC5) into one nobody can satisfy
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_verify_every_line.py::VerifyEveryLineTests::test_two_passing_lines_pass_once

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
| 2026-09-25 | sdlc-studio v6 planning | QA seat: generic AC1 replaced with falsifiable criteria for Sprint 5; fix chosen is run every line (no new refusal, LC-008) |
