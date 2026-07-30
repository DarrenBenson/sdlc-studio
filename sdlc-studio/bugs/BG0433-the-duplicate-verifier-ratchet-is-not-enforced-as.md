# BG0433: the duplicate-verifier ratchet is not enforced as a ratchet, groups on a weaker key than the command it runs, and cannot notice its own flag going away

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, tools/tests/test_baselines_only_shrink.py, tools/tests/test_precommit_lane_order.py, .githooks/pre-commit, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** Executed by an independent reviewer, including a control-vs-mutant run on a copied tree for the --bugs case.
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch); agent; skill v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

Three defects in one lane. (1) `sdlc-studio/.verify-lint-baseline.json` is absent from `tools/tests/test_baselines_only_shrink.py`'s BASELINES tuple, and that guard's entry reader is a line-splitter that could not parse JSON if it were added - so the shrink-only rule stated in AGENTS.md and in the hook lane's own text is prose. A brand-new duplicate group plus a hand-written baseline entry passes with `ratchet clean`, exit 0. (2) `dup_group_key` normalises whitespace and lowercases the verb, while the executed command goes through `shlex.split`: `pytest X` and `pytest 'X'` are byte-for-byte the same subprocess and form two groups of one, reported as no duplicate at all - the exact failure the key's docstring claims to have closed. (3) Dropping `--bugs` from the hook lane leaves all fourteen lane-order tests green; the sibling lens-signature lane HAS that guard, and its docstring names this lane as the motivating case.

## Steps to Reproduce

1. Add a baseline entry for a new shared selector - `lint --ratchet` reports clean.
2. Two ACs with selectors `pytest X` and `pytest 'X'` - no group reported, identical argv.
3. Remove `--bugs` from .githooks/pre-commit - `tools.tests.test_precommit_lane_order` still 14 tests OK.

## Proposed Fix

Add the JSON baseline to the shrink guard with a reader that can parse it; group on the resolved argv rather than on a normalised string; assert the ratchet lane's flags at both invocation sites as the lens-signature lane does.

## Acceptance Criteria

- [ ] The behaviour described is corrected: Three defects in one lane.
- [ ] The proposed fix lands, pinned by a test: Add the JSON baseline to the shrink guard with a reader that can parse it; group on the resolved argv rather than on a normalised string; assert the ratchet...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch) | Filed |
