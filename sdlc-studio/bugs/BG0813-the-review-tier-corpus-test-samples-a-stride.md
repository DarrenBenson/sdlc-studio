# BG0813: The review-tier corpus test samples a stride of the live corpus, so every new artefact moves the sample and it goes red with no code change

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_critic.py, changelog.d/BG0813.md
> **Evidence:** skill suite on main 2026-09-28 (BG0812 builder, reproduced by the orchestrator): AssertionError 0 not greater than 0 at test_critic.py:585
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T09:18:43Z

## Summary

`test_critic.py::BriefTierTests::test_the_corpus_spans_more_than_one_band` takes every Nth story and bug in this repository (24 units, stride len/24) and asserts at least one bands light and one full. Each artefact filed shifts the stride, so the sampled set changes with no code change: on 2026-09-28, after this sprint filed BG0810-BG0812, all 24 sampled units band full and the test fails ('no unit in 24 bands light - the tiering is a no-op') although the tiering is not a no-op. It was green at the last push (36995de6). The push's full suite would refuse the next push on it.

## Steps to Reproduce

Run pytest .claude/skills/sdlc-studio/scripts/tests/`test_critic.py`::BriefTierTests::`test_the_corpus_spans_more_than_one_band` on main after filing a few artefacts.

## Proposed Fix

Walk the corpus in a fixed, stride-free order and stop as soon as both a light and a full unit are seen, bounded (e.g. 150 units); fail only if the bound is reached without both. The claim stays the same - the tiering is not a no-op on this corpus - but the sample no longer moves with each filing.

## Acceptance Criteria

- [ ] **AC1** Given this repository's corpus, when the test runs, then it passes as long as the corpus holds at least one light and one full unit among its first 150 in a fixed order, whatever artefacts were filed since. Fails on: the stride sample, which goes red when a filing shifts it onto 24 full units
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BriefTierTests::test_the_corpus_spans_more_than_one_band
  - **Verified:** yes (2026-09-28)
- [ ] **AC2** Given a corpus mutant where every band maps to full (or every band to light), then the test still fails. Fails on: a rewrite that stops asserting both directions

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
