# BG0067: verify_ac pytest -k DSL glues path and marker into one argv element

> **Status:** Closed
> **Created:** 2026-07-08
> **Created-by:** sdlc-studio new
> **Severity:** Medium

## Summary

`verify_ac.py`'s DSL builder mishandles the `pytest <path> -k <marker>` Verify
form: it passes the entire tail (path + flag + marker) as a single argv
element, so pytest receives one nonexistent "file" instead of a path and a
`-k` flag - every such Verify line false-fails with a misleading "file or
directory not found" error, even when the referenced test file exists and
would otherwise collect fine.

## Affected Area

- **Component:** `scripts/verify_ac.py` (`_build_command`, the `pytest` DSL verb)

## Environment

- **Version:** 3.6.0
- **Platform:** local dev machine (Linux); surfaced only once a local `pytest`
  was actually installed (it had been broken/absent, masking this bug entirely -
  every pytest-backed Verify line failed for a different reason until then)

---

## Steps to Reproduce

1. Author a story AC with `Verify: pytest <path> -k <marker>` (the two-token
   form with a space, as used by e.g. US0068, US0076-US0082's ACs)
2. Run `verify_ac.py run --id <that story>`
3. Observe `FAIL ... ERROR: file or directory not found: <path> -k <marker>` -
   the whole string glued together as one path, even though `<path>` exists

## Expected Behaviour

pytest receives the path and `-k <marker>` as separate argv elements
(`["pytest", "-q", "<path>", "-k", "<marker>"]`), so it either collects and
runs the matching test(s) or correctly reports "0 selected" / a real failure -
never a false "file not found".

## Actual Behaviour

`_build_command` returned `["pytest", "-q", tail]` where `tail` is the
unsplit remainder after `"pytest "` - e.g.
`".claude/skills/sdlc-studio/scripts/tests/test_config.py -k override_warn"`
as one string. pytest then tried to open a file literally named that whole
string and failed.

---

## Root Cause Analysis

The `pytest` branch of `_build_command` (scripts/verify_ac.py, ~line 297) was
never updated to split `tail` when the DSL grew the `-k`-flag form - the `go`
verb one branch below it (`["go", "test"] + shlex.split(tail)`) already does
this correctly and was the reference for the fix. The bug was invisible until
now because this machine's local `pytest` binary was itself broken
(`ModuleNotFoundError`), so every pytest-backed Verify line failed for that
reason first - fixing the environment gap surfaced the latent DSL bug.

## Proposed Fix

Split `tail` with `shlex.split` before appending, matching the `go` verb:
`["pytest", "-q"] + shlex.split(tail)`.

### Files Modified

- `.claude/skills/sdlc-studio/scripts/verify_ac.py` - `_build_command`'s `pytest` branch now uses `shlex.split(tail)` instead of the raw unsplit `tail`
- `.claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py` - new regression test

### Tests Added

- `test_build_command_pytest_with_k_flag_splits_into_separate_args` (`test_verify_ac.py`) - asserts `pytest <path> -k <marker>` builds `["pytest", "-q", "<path>", "-k", "<marker>"]`, not a glued single element

---

## Verification

- [x] Fix verified in development
- [x] Regression tests pass (1249/1249 script tests green)
- [x] No side effects observed (existing `test_build_command_pytest` node-id case, which has no space in `tail`, is unaffected)
- [x] **Mutation-checked** - the new regression test was run against the unfixed code first (`["pytest", "-q", tail]`) and failed with the exact glued-string mismatch (`AssertionError: Lists differ` showing the combined string vs the expected split list); restoring the fix turned it green. Record: confirmed red-then-green in the same session, no separate mutation script run (a plain assertion diff, not a subtler behaviour, made the manual check unambiguous).

**Verified by:** main-loop:claude-sonnet-5
**Verification date:** 2026-07-08
**Verification depth:** functional

> Verification depth tiers: `smoke` (one-shot ping) | `functional` (single round-trip) | `conversational` (multi-turn / multi-step) | `soak` (live traffic over a window) | `live` (operator-confirmed in production with no rollback). See `reference-test-best-practices.md#verification-depth-tiers`. A bug cannot be marked **Fixed** until depth is at least `functional`; promoting **Fixed** to **Verified** requires a tier ABOVE functional (`conversational`/`soak`/`live` - Verified claims the higher-tier proof landed). A production-affecting bug (declare it with a `> **Production-affecting:** yes` header field) cannot be **Closed** until depth is at least `soak` (default 7 days). **These tiers are enforced**: `transition.py` refuses a Fixed/Verified/Closed transition that under-shoots them (a missing depth field is refused, not assumed) - `--force` records an override.
>
> **The regression test must be mutation-checked** (above): a test added alongside a fix but never seen to fail may be asserting the wrong thing and would not catch the bug's return. Seeing it red against the unfixed code is the proof it pins the fix. See `reference-test-best-practices.md#mutation-check`.

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-08 | post-fix: local pytest install exposed the bug | Bug reported and fixed same-session (shlex.split fix + regression test) |
