# BG1141: The gate-host docs test's docstrings claim more than it samples: values of SDLC_GATE_LOCAL other than 1, and keys read as `git -C <dir> config`

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_lean_gate_host_docs.py, changelog.d/BG1141.md
> **Evidence:** sdlc-studio/reviews/critic-verdicts.md, US1086 APPROVE round 3 by qa-seat-US1086-r1 (brief cb199b50d86d): mutants H6t, H6n, A6 and A6b survive.
> **Created:** 2026-10-31
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-31T22:54:34Z

## Summary

qa-seat-US1086-r1's round-3 APPROVE of US1086 (2026-10-31) found two low over-claims in tools/tests/`test_lean_gate_host_docs.py.` The AC2 docstring (:199-202) says a hook honouring a value of `SDLC_GATE_LOCAL` other than 1 fails the test, but the cases (:42-45) try only unset, empty, yes and 0, so a hook that also honours `true` or reads `01` as 1 passes. The AC1 derivation (:118) matches only `git` directly followed by `config`, so a key read as `git -C "$dir" config --get sdlc.x` is not derived, while the module docstring (:6) and the `_settings` docstring (:112) say every key on a line that runs git config is read. remote-gate.sh already uses the `git -C` form for its other git calls.

## Steps to Reproduce

1. In a throwaway worktree, add `[ "${SDLC_GATE_LOCAL:-}" != "true" ]` beside the existing check at .githooks/pre-push:46; run `test_lean_gate_host_docs.py`: green.
2. Add `git -C "$dir" config --get sdlc.gateUser` to tools/remote-gate.sh; run it: green, the key underived.
3. Expected: both fail, or the docstrings name only what the test samples.

## Proposed Fix

Add near-miss cases (`true`, `01`) to the `SDLC_GATE_LOCAL` rows, and let the key derivation accept git's global options before `config` (`-C <dir>`, `-c k=v`), each with a fixture line that kills its mutant. Or narrow both docstrings to what is sampled.

## Acceptance Criteria

- [ ] **AC1** A hook that runs locally for an `SDLC_GATE_LOCAL` value other than the literal 1 (`true`, `01`) fails the test.
  - **Verify:** pytest tools/tests/test_lean_gate_host_docs.py
- [ ] **AC2** A key read as `git -C <dir> config --get sdlc.<key>` is derived as a setting, and a key read through a shell variable is still out of reach, as the docstring says.
  - **Verify:** pytest tools/tests/test_lean_gate_host_docs.py

## Impact

Low: no script reads a key in the -C form today, and the hook compares the literal string 1. Two sentences in a test docstring are false, and a reader would trust them (LC-018).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-31 | claude | Filed |
