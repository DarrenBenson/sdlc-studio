# BG0434: two of the four signature detector shapes are exercised only by a synthetic fixture, and the one real row's path resolves anywhere

> **Status:** Fixed
> **Verification depth:** functional + mutation (each of the four runners deleted in turn -> all KILLED; bash and npm previously caught by nothing a real pack could notice)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/templates/audit-profiles/code.md, .claude/skills/sdlc-studio/scripts/readiness.py, .claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py, .claude/skills/sdlc-studio/scripts/tests/test_readiness.py
> **Evidence:** Executed by an independent reviewer, who separately CONFIRMED the consuming-project resolution claim holds for the detectors that do ship.
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch); agent; skill v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

The story's AC2 requires at least one real pack row per detector shape, on the stated ground that a widened classifier whose only exerciser is its own unit test is the over-engineering lens pointed at the change. Dumping all twenty signature cells across the five shipped packs: `rg` has one row, `bash` and `npm` have NONE. So two of the four runners in `SIGNATURE_DETECTORS` are exercised only by the fixture list in the test - and that fixture's `bash` entry is a repo-local path that could never ship in a pack. The AC is stamped verified. Compounding: the single `rg` row's extracted path is `.`, which resolves against any root, so the on-disk rule is vacuous for the one row exercising the path-last shape.

## Steps to Reproduce

1. Extract the Signature cell from every lens row in templates/audit-profiles/*.md.
2. Count by leading runner: bash=0, npm=0, rg=1, python3=rest.
3. The rg row's path component is `.`.

## Proposed Fix

Author a real pack row per shape with a target that travels to a consuming project, or narrow `SIGNATURE_DETECTORS` to the shapes the packs actually use and say so.

## Acceptance Criteria

### AC1: every detector shape is exercised through the shipped parser

- **Given** each of the four documented detectors
- **When** a signature using it is parsed
- **Then** it is recognised, asserted once per runner - because `all(mechanical)` over the shipped packs passes with the two unused runners removed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_readiness.py::SignatureDetectorCoverageTests::test_each_detector_is_recognised_by_the_shipped_parser
- **Verified:** yes (2026-08-02)

### AC2: a bare npm is still refused

- **Given** `npm lint`, with no `run`
- **When** it is parsed
- **Then** it is not mechanical, because `npm` alone runs an install rather than a check
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_readiness.py::SignatureDetectorCoverageTests::test_a_bare_npm_is_still_refused
- **Verified:** yes (2026-08-02)

### AC3: a detector named mid-sentence is not a signature

- **Given** a prose reason mentioning a detector token
- **When** it is parsed
- **Then** it is not mechanical, which is the only shape that catches a widened head test
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_readiness.py::SignatureDetectorCoverageTests::test_a_detector_named_mid_sentence_is_not_mechanical
- **Verified:** yes (2026-08-02)

> **Measured, and the tuple deliberately NOT narrowed.** The shipped packs use `python3` (8
> rows) and `rg` (1); `bash` and `npm` appear in none. Narrowing to what this repo happens to
> use would remove vocabulary a consuming project writes its own signatures in, so the coverage
> gap is closed by exercising each shape against the real parser instead. Mutation-verified:
> dropping ANY one of the four runners is now KILLED; before, `bash` and `npm` were caught by
> nothing a real pack could notice.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch) | Filed |
