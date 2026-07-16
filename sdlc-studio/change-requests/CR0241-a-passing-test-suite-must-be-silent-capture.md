# CR-0241: A passing test suite must be silent: capture tool stdout in the validator's own tests

> **Status:** Complete
> **Size:** S
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Priority:** P3
> **Type:** quality

## Summary

The skill suite prints ERROR lines on a GREEN run. validate.py's unit tests feed it a deliberately-bad fixture story (US0001-bad.md, status Frozen, no ACs) and assert it reports errors; the tool's diagnostics are not captured, so they escape to the console. 2011 tests pass and the tail of the output reads like a failure. It cost a full re-run to establish the suite had passed, and in CI a real error would sit camouflaged in a crowd of expected ones. Capture the subprocess/stdout in those tests so a passing run says nothing.

## Impact

Noise on a green run trains everyone - human and agent - to ignore ERROR lines, which is the exact reflex that lets a real one through. Adjacent to LL0009: a signal that cannot be distinguished from noise is not a signal.

**Effort:** S

## Acceptance Criteria

- [ ] **AC1:** A passing run of the skill suite prints no `ERROR` line at all. This is the whole
      point: on green, the tool's expected diagnostics are captured by the test that provoked
      them, not printed into the operator's terminal.
- [ ] **AC2:** The suite still passes, and still fails when the bad fixture is accepted - the fix
      captures output, it does not weaken the assertions that reject the fixture.
- [ ] **AC3:** The bad-fixture tests still assert on the diagnostics they captured (the
      `status-vocab` and `no-ac` rules among them), so coverage of the validator's error paths is
      unchanged rather than silenced.
- [ ] **AC4:** The same treatment reaches every shipped script whose tests leak diagnostics on a
      green run, `tools/` included - not only `validate.py`. An enumerated fix exempts the one it
      forgot (LL0013), so a clean run of the whole suite is the criterion, not a clean run of the
      file that was noticed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Created via `new` (deterministic) |
