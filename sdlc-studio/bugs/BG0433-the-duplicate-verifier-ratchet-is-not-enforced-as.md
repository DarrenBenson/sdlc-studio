# BG0433: the duplicate-verifier ratchet is not enforced as a ratchet, groups on a weaker key than the command it runs, and cannot notice its own flag going away

> **Status:** Fixed
> **Verification depth:** functional (the reader asserted against the line-split answer it replaces, every declared baseline asserted non-empty, and both lane invocation sites pinned)
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

### AC1: the JSON baseline is parsed, and every declared baseline holds entries

- **Given** `.verify-lint-baseline.json`, absent from the shrink guard because the line-splitting reader could not have parsed it
- **When** the guard reads it
- **Then** it yields real group keys rather than JSON punctuation, and every file declared a baseline parses to a non-empty set - one that parses to nothing passes every comparison and ratchets nothing
- **Verify:** pytest tools/tests/test_baselines_only_shrink.py::JsonBaselineReaderTests::test_the_json_baseline_is_parsed_into_real_entries
- **Verified:** yes (2026-08-02)

### AC2: a declared baseline that cannot be read is caught

- **Given** the BASELINES tuple
- **When** each file is parsed
- **Then** none yields an empty set, because a baseline in the tuple that parses to nothing is exactly the state this bug found - present, green and holding nothing
- **Verify:** pytest tools/tests/test_baselines_only_shrink.py::JsonBaselineReaderTests::test_every_declared_baseline_is_readable
- **Verified:** yes (2026-08-02)

### AC3: the ratchet lane's flags are asserted at BOTH invocation sites

- **Given** the pre-commit hook and `package.json`
- **When** the `verify-ratchet` lane is read at each
- **Then** both carry `--ratchet` and `--bugs` - without the first the lint reports and never refuses, without the second it judges stories only and half the corpus is silently exempt. This is the lane that already lost `--bugs` once with the whole suite green
- **Verify:** pytest tools/tests/test_precommit_lane_order.py::LensSignatureLaneTests::test_the_ratchet_lane_carries_its_flags_at_both_invocation_sites
- **Verified:** yes (2026-08-02)

> The third defect in the filing - grouping on the resolved argv rather than a normalised
> string - is NOT delivered here. It is a change to how duplicate verifiers are grouped, and it
> would reshape the baseline this unit just brought under the ratchet; doing both in one step
> would leave neither measurable - the new grouping's yield could not be told from
> this one's. Carved out to [BG0486](BG0486-duplicate-verifiers-are-grouped-on-a-normalised-string.md)
> rather than quietly dropped.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch) | Filed |
