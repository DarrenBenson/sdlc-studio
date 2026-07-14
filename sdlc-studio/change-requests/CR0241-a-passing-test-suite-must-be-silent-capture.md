# CR-0241: A passing test suite must be silent: capture tool stdout in the validator's own tests

> **Status:** Proposed
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Priority:** P3
> **Type:** quality

## Summary

The skill suite prints ERROR lines on a GREEN run. validate.py's unit tests feed it a deliberately-bad fixture story (US0001-bad.md, status Frozen, no ACs) and assert it reports errors; the tool's diagnostics are not captured, so they escape to the console. 2011 tests pass and the tail of the output reads like a failure. It cost a full re-run to establish the suite had passed, and in CI a real error would sit camouflaged in a crowd of expected ones. Capture the subprocess/stdout in those tests so a passing run says nothing.

## Impact

Noise on a green run trains everyone - human and agent - to ignore ERROR lines, which is the exact reflex that lets a real one through. Adjacent to LL0009: a signal that cannot be distinguished from noise is not a signal.

**Effort:** {{S|M|L}}

## Acceptance Criteria

- [ ] **AC1:** A passing run of the skill suite emits no `ERROR` line. This is the whole point:
      on green, the tool's expected diagnostics are captured by the test, not printed.
      Verify: `python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests 2>&1 | grep -q '^ERROR' && exit 1 || exit 0`
- [ ] **AC2:** The suite still passes - the fix captures the output, it does not weaken the
      assertions that the bad fixture is rejected.
      Verify: `python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests`
- [ ] **AC3:** The bad-fixture tests still assert on the diagnostics they captured, so coverage of
      the validator's error paths is unchanged rather than silenced.
      Verify: `rg -q 'status-vocab|no-ac' .claude/skills/sdlc-studio/scripts/tests`
- [ ] **AC4:** The same treatment is applied to any other shipped script whose tests leak
      diagnostics on a green run, not only `validate.py` - an enumerated fix exempts the one it
      forgot (LL0013).
      Verify: `python3 -m unittest discover -s tools/tests 2>&1 | grep -q '^ERROR' && exit 1 || exit 0`

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Created via `new` (deterministic) |
