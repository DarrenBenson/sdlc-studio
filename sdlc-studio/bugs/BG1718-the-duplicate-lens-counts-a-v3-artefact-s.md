# BG1718: The duplicate lens counts a v3 artefact's own ULID suffix as a word, so two v3 duplicates score lower than the same pair with v2 ids

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/backlog_triage.py, .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py, changelog.d/BG1718.md
> **Evidence:** backlog_triage.py:77 `_ID_TOKEN_RE = re.compile(r"^(?:us|bg|ep|cr|rfc|is|pl|ts|wf)\d{3,}$")` and :80 `_tokens`; lib/sdlc_md.py:37 documents the v3 form `BG-01JQK3F8`. Found by the qa seat grooming US1324 on 2026-11-23.
> **Created:** 2026-11-23
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-23T02:51:36Z

## Summary

`backlog_triage._tokens` drops an artefact's own id token so that two duplicates carrying different ids are not driven apart, but its `_ID_TOKEN_RE` matches only the v2 shape (a type prefix and digits). A v3 id such as BG-01JQK3F8 splits into `bg`, dropped for length, and `01jqk3f8`, which is kept as a word. Each artefact's suffix is unique, so it adds one token to each side of the Jaccard union and none to the intersection, and a v3 project's duplicate lens reports a near-duplicate below the bar that the same pair with v2 ids reaches.

## Steps to Reproduce

1. In a v3 project, file two bugs with the same title and summary. 2. Run the duplicate lens over the backlog (`backlog_triage).` 3. Compare the pair's score with the same pair in a v2 project.

## Proposed Fix

Drop the artefact's own id token in either shape: match the v3 suffix by reading the id from the H1 prefix (`sdlc_md`'s id pattern) rather than by a v2-only regex, so only the artefact's own id is removed and other words survive.

## Acceptance Criteria

- [ ] **AC1** A v3 id suffix is not a token: given two bugs in a v3 project whose H1 titles differ only in their ids (`BG-01JQK3F8` and `BG-01JQK3G2`), when the duplicate lens scores the pair, then the score equals the score of the same pair titled `BG0001` and `BG0002`. Fails on: the v3 pair scoring lower, or either suffix appearing in `_tokens`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py::V3IdTokenTests::test_a_v3_id_suffix_is_not_a_token
  - **Verified:** yes (2026-11-23)
- [ ] **AC2** A word that only looks like a suffix is kept: given a title holding an eight-character word of digits and letters that is not the artefact's id (for example `sha256ab`), when `_tokens` reads it, then the word is kept. Fails on: dropping every eight-character alphanumeric word.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py::V3IdTokenTests::test_a_non_id_word_is_kept
  - **Verified:** yes (2026-11-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-23 | sdlc-studio | Filed |
