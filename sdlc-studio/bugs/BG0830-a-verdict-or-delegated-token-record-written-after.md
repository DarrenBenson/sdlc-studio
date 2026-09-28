# BG0830: A verdict or delegated-token record written after the seal lands on the sealed run without a warning

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_sealed_run_writes.py, changelog.d/BG0830.md, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Evidence:** soak F28; BG0797 round-2 review; HEAD 7e53a438 run_state.py:1453-1490 (only `run_id` checked) and critic.py (no sealed or terminal check before writing)
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:26:33Z

## Summary

`critic.py record` wrote a second verdict from a different reviewer on a unit already Done in a sealed run, with no warning (soak F28). `run_state.record_delegated_tokens` checks only that a `run_id` exists: after the close it records onto a sealed or closed-not-archived run, and once the next run opens it records there, so a late record either moves a signed run's delegated figures or is booked to the wrong run (BG0797 r2 review). The `--delegated-tokens`/`--delegated-unit` flags are also missing from the toolchain runbook and help (LC-003).

## Steps to Reproduce

Seal a run with `sprint sign`; then `critic.py record --unit <a Done unit> --verdict APPROVE ...` and `retro.py accuracy --delegated-tokens 100 ...`: both write, silently.

## Proposed Fix

One `run_state` guard, `refuse_if_sealed`: a record against a sealed run is refused naming `sprint reopen`; a verdict on a unit already terminal warns. Add the delegated flags to the runbook's close rows.

## Acceptance Criteria

- [ ] **AC1** Given a sealed run, when `record_delegated_tokens` or `critic.py record` targets it, then the write is refused naming `sprint reopen`. Fails on: HEAD, which writes
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sealed_run_writes.py::SealedRunWritesTests::test_a_record_after_the_seal_is_refused
- [ ] **AC2** Given reference-sprint-toolchain.md, then the delegated-agent record command is listed. Fails on: HEAD
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sealed_run_writes.py::SealedRunWritesTests::test_the_runbook_names_the_delegated_record

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
