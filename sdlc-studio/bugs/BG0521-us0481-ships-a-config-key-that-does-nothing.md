# BG0521: US0481 ships a config key that does nothing at plan time, and batch add writes the unit before it refuses it

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/help/sprint.md
> **Evidence:** Independently established by the QA and engineering review seats at the RUN-01KZ79C1 batch boundary, each by execution against isolated fixtures, and each reporting `affects_check_mode`'s single call site at sprint.py:7179 inside cmd_batch.
> **Created:** 2026-08-05
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Three defects, found by both adversarial seats independently at the RUN-01KZ79C1 boundary.

1. `sprint.affects_check` is INERT for `sprint plan`. `affects_check_mode` has exactly one call site - `cmd_batch`. `cmd_plan` renders the pre-existing advisory and never consults it. Executed: a plan over an offending unit produces byte-identical output under `warn` and under `block`, exiting 0 in both, printing the literal `advisory - nothing is refused`. US0481 AC4's Given is the setting absent, warn and block; its When is a plan running under each. That behaviour does not exist.

2. `batch add` under `block` WRITES BEFORE IT REFUSES. `run_state.add_to_batch` runs, the unit is appended to `batch` and to `batch_changes`, the message says it was added, and only then does the mode check print a refusal and exit 2. So a unit the operator was told was refused is in the batch the done-gate reads. This is the same write-above-the-check shape as BG0507, which was fixed in this same batch.

3. The `--format json` path skips the check entirely: the refusal sits in the text-render `else` branch, so a JSON invocation adds the unit, exits 0, and reports no finding.

`help/sprint.md` documents the setting as deciding what a finding does, for both verbs. It decides nothing for `plan`, and only what is printed after the write for `batch add`.

## Steps to Reproduce

1. Fixture with a unit whose `Verify:` targets a file its `Affects` omits.
2. `sprint.py plan --bugs Open --write` with `sprint.affects_check` absent, then `warn`, then `block` - diff the three outputs. They are identical, all rc 0.
3. With `block` set and a run open: `sprint.py batch add BG0001` - rc 2 with a refusal printed, and the unit present in `run-state.json`'s `batch` and `batch_changes`.
4. The same `batch add --format json` - rc 0, unit added, no finding reported.

## Proposed Fix

Call the shared resolver from `cmd_plan` and honour the mode there, which is what AC4 describes. Move the `batch add` check ABOVE `run_state.add_to_batch` so a refused unit is never written - the ordering is the guard, exactly as BG0507 established. Hoist the check out of the text-render branch so the JSON path is covered. Then pin AC4 by RUNNING A PLAN under each of the three settings, not by asserting the getter returns a string: the shipped verifier does the latter and passes while the behaviour is absent.

## Acceptance Criteria

- [ ] The behaviour described is corrected: Three defects, found by both adversarial seats independently at the RUN-01KZ79C1 boundary.
- [ ] The proposed fix lands, pinned by a test: Call the shared resolver from `cmd_plan` and honour the mode there, which is what AC4 describes.

## Impact

An operator who sets `block` believes ungroomed `Affects` declarations are being refused at plan time. Nothing is. Worse, the one place the setting is honoured leaves the unit in the batch after saying it refused it, so the done-gate reads a unit the operator believes was rejected.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Filed |
