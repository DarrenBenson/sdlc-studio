# BG1644: MarkdownEvidenceLintTests reads the live sdlc-studio/reviews/ tree, so committing the author-mutant records turns the push gate red

> **Status:** Fixed
> **Severity:** High
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T01:15:54Z

## Summary

`test_verify_ac.py`'s `MarkdownEvidenceLintTests.test_every_escape_found_by_review_is_refused` lints 'grep "anything" sdlc-studio/reviews/' and 'sdlc-studio/reviews/*' against the real repository root (`_root`() is parents[5]) and expects a refusal, because the directory once held only markdown. The TRD's committed-records table lists sdlc-studio/reviews/author-mutants/<id>.json, and RUN-01M7TTK3's paperwork commit 700d3466 is the first to commit those JSON records: `verify_ac`'s all-or-nothing rule now correctly sees a non-markdown file and returns None, and the push boundary gate on devserver1 refused 700d3466 with 2 failed. The test's verdict depends on what the repository happens to hold, not on the lint.

## Steps to Reproduce

With sdlc-studio/reviews/author-mutants/*.json committed, run pytest .claude/skills/sdlc-studio/scripts/tests/`test_verify_ac.py` -k `test_every_escape_found_by_review_is_refused`: 2 subtests fail with AssertionError: unexpectedly None.

## Proposed Fix

Give MarkdownEvidenceLintTests a temporary root that holds a markdown-only sdlc-studio/reviews/ (and the other directories its escapes name), so each escape is judged against a fixture the test controls, and add a positive control: the same grep over a fixture reviews/ holding a .json file is not refused.

## Acceptance Criteria

- [ ] **AC1** Given a repository whose `sdlc-studio/reviews/` holds committed JSON records beside its markdown, when `MarkdownEvidenceLintTests` runs, then every escape it lists is judged against a temporary root the test builds (a markdown-only `sdlc-studio/reviews/` and the other directories its escapes name), and each is refused.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::MarkdownEvidenceLintTests::test_every_escape_found_by_review_is_refused
  - **Verified:** yes (2026-11-20)
- [ ] **AC2** Fails on: pointing the escapes back at the live repository root, or a fixture `reviews/` holding a `.json` file being refused; the positive control lints the same grep over a fixture `reviews/` that holds a `.json` record and expects no refusal.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::MarkdownEvidenceLintTests::test_a_reviews_tree_holding_a_json_record_is_not_refused
  - **Verified:** yes (2026-11-20)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
