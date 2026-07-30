# BG0434: two of the four signature detector shapes are exercised only by a synthetic fixture, and the one real row's path resolves anywhere

> **Status:** Open
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

- [ ] The behaviour described is corrected: The story's AC2 requires at least one real pack row per detector shape, on the stated ground that a widened classifier whose only exerciser is its own unit...
- [ ] The proposed fix lands, pinned by a test: Author a real pack row per shape with a target that travels to a consuming project, or narrow `SIGNATURE_DETECTORS` to the shapes the packs actually use and...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch) | Filed |
