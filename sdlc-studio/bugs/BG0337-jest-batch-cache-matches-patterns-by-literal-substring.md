# BG0337: Jest batch cache matches patterns by literal substring where jest -t is a regex, so cached and authoritative verdicts ca

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5); agent; skill v5.0.0

## Summary

The cache resolver claims to mirror jest -t but uses Python substring containment ('pat in a["name"]') where jest treats -t as a testNamePattern regex; a metacharacter-bearing pattern that literally occurs in some passing assertion name yields a green cached verdict computed over a different test set than jest would select, and under --release the batch cache substitutes for the authoritative run in a blocking gate lane.

## Steps to Reproduce

Evidence (`resolve_jest_from_cache`, lines 1132-1145): Confirmed at `verify_ac.py` 1132-1145: docstring says 'mirroring jest -t', implementation is substring containment; the pytest cache path by contrast refuses anything but a bare node id.

## Proposed Fix

Match with re.search(pat, name) to mirror jest's testNamePattern semantics, and on re.error (invalid regex) return None so the caller falls back to the authoritative per-AC jest subprocess.

## Acceptance Criteria

### AC1: a pattern selects the tests `jest -t` would select

- **Given** cached assertions `renders the total` (failing) and `renders the totals` (passing), and the pattern `renders the total$`
- **When** the cache resolves the verifier
- **Then** the verdict is not-ok, because the anchor selects only the red test - substring containment reported green
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::JestBatchTests::test_a_pattern_is_a_regex_not_a_literal_substring

### AC2: an unparseable pattern is not a verdict

- **Given** a pattern that Python cannot compile, occurring literally in a passing assertion name
- **When** the cache resolves the verifier
- **Then** it returns None so the caller falls through to the authoritative per-AC subprocess
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::JestBatchTests::test_an_invalid_regex_falls_back_to_the_authoritative_run

### AC3: an ordinary plain-text pattern still resolves from the cache

- **Given** a pattern with no metacharacters naming a passing assertion
- **When** the cache resolves the verifier
- **Then** it still returns a pass, so the batch saving is kept
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::JestBatchTests::test_a_plain_pattern_still_resolves

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5) | Filed |
| 2026-07-28 | delivery lane (RUN-01KYJZGZ) | Acceptance criteria authored; regex matching plus invalid-pattern fall-through landed |
