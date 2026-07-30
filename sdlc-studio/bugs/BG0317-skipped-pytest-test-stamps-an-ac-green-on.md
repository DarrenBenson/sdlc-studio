# BG0317: Skipped pytest test stamps an AC green on the default verify path while batch mode fails it

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0
> **Audit-lens:** unknown
> **Audit-run:** wf_804ef18d

## Summary

A pytest verifier whose target test is skipped exits 0 with '1 skipped', evades the vacuity regex, and is stamped Verified: yes by the default per-AC path - so an AC whose test never ran passes the Done gate - while the batch path (used by gate --release) reads the same run from JUnit XML, treats the skip as not-passed, and reports a hard failure with the misleading message 'cached pytest failure'. Identical inputs, opposite verdicts.

## Steps to Reproduce

Evidence (`_PYTEST_ZERO` / `run_verifier` (lines 228, 356-366) vs `_parse_junit_xml` (line 1016) and `resolve_pytest_from_cache` (lines 1101-1129)): Reproduced: `run_verifier` on a @pytest.mark.skip node returns ok=True, vacuous=False ('1 skipped' does not match `_PYTEST_ZERO)`; `resolve_pytest_from_cache` on the same node returns ok=False citing `_parse_junit_xml`:1016's 'A skip is NOT a pass' rule.

## Proposed Fix

Parse pytest's summary line in `run_verifier` and treat an exit-0 run whose selected tests were all skipped as vacuous/not-passed, matching the JUnit path; also reword the cached-path message to say 'skipped' rather than 'failure'.

## Acceptance Criteria

### AC1: an all-skipped run is not a pass

- **Given** the defect as filed in Steps to Reproduce
- **When** the repair is in place
- **Then** the behaviour is the one the Proposed Fix describes, proven by a test written red before the fix
- **Proven by:** `pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::SkippedPytestVerifierTests::test_an_all_skipped_run_is_not_a_pass`, written red before the fix and green after
- **Verified:** yes (2026-07-27, functional)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
| 2026-07-27 | Claude Fable 5 | Affects corrected to the fix footprint incl. its test file (BG0343: the filer wrote the evidence location) |
