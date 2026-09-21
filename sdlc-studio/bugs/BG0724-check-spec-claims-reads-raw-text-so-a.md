# BG0724: check_spec_claims reads raw text, so a claim inside a fenced code block is judged as a live claim

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** tools/check_spec_claims.py, tools/tests/test_check_spec_claims.py
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0463 claim 7, confirmed by execution at HEAD. `check()` passes raw `text` to `claims_in()`, while `_FENCE_RE` is defined and referenced nowhere - the only occurrence in the file is its own definition. Executed: `claims_in` over a fenced line reading `scripts/ (999+ scripts)` returns a live band claim, while `_live_lines` correctly drops it. So an EXAMPLE in documentation - the place a deliberately wrong number is most likely to appear - is checked as though it were an assertion about the tree.

## Steps to Reproduce

1. Put a line claiming a false census inside a fenced block in any checked markdown file. 2. Run `python3 tools/check_spec_claims.py`. 3. It reports the fenced example as a claim. 4. `grep -n _FENCE_RE tools/check_spec_claims.py` -> one hit, its own definition.

## Proposed Fix

Route `check()` through `_live_lines` (or have `claims_in` take live lines), and delete `_FENCE_RE` once it is genuinely unused. Pin with a fenced-band fixture that must NOT be reported, beside the unfenced positive control that must be.

## Acceptance Criteria

### AC1: a claim inside a fenced block is not read as a live claim

- **Given** a checked markdown file carrying a deliberately false census inside a fenced code block, and the same claim unfenced beneath it as the positive control
- **When** `check_spec_claims` runs
- **Then** the unfenced claim is reported and the fenced one is not - an example is not an assertion
- **Mutant:** in `tools/check_spec_claims.py`, pass raw `text` to `claims_in()` rather than the live lines, which is the shipped behaviour: `_FENCE_RE` is then defined and referenced nowhere and every documented example is judged as a claim about the tree
- **Verify:** pytest tools/tests/test_check_spec_claims.py::FencedClaimTests::test_a_fenced_claim_is_not_live_and_its_unfenced_control_is

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Filed |
