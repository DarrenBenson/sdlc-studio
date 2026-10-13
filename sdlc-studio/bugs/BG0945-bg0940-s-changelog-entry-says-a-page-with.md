# BG0945: BG0940's changelog entry says a page with a late ruling is signed, though sign refuses until the run is re-closed

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** changelog.d/BG0940.md, .claude/skills/sdlc-studio/scripts/tests/test_bg0940_fragment_matches_sign.py, changelog.d/BG0945.md
> **Created:** 2026-10-05
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-05T07:47:09Z

## Summary

Found by the QA review of BG0940 (qa-s12-bg0940, RUN-01M45FV6), filed under D0338. changelog.d/BG0940.md says the filed page 'still checks VALID when it is signed', but through the CLI the ruling's decisions.md row trips sign's existing tree check (sign REFUSED: sdlc-studio/decisions.md), so the run cannot be signed without a re-close, and the re-filed page still omits the withheld ruling. The VALID half is true; the sign half over-claims.

## Steps to Reproduce

In a fixture: sprint close, decisions.py add --by operator, sprint sign: refused naming sdlc-studio/decisions.md.

## Proposed Fix

Reword the fragment to what happens: the page stays VALID, sign refuses the changed tree as before, and a re-close files a page that does not count the late ruling.

## Acceptance Criteria

- [ ] **AC1** Given a fixture run closed, then a ruling added with `decisions.py add --by operator`, when `sprint sign` runs through the CLI, then it refuses naming `sdlc-studio/decisions.md`, and `changelog.d/BG0940.md` says that sign refuses the changed tree until a re-close and no longer says the page is signed after a late ruling. Fails on: the current 'still checks VALID when it is signed' wording
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_bg0940_fragment_matches_sign.py::FragmentMatchesSignTests::test_the_fragment_says_what_sign_does
  - **Verified:** yes (2026-10-13)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-05 | sdlc-studio | Filed |
| 2026-10-12 | Claude Opus 5.5 (planning) | Affects names the unit's changelog fragment, before the first 6.2 run (D0365) |
| 2026-10-12 | Claude Opus 5.5 (planning) | Goal review: Verify proves the sentence by running its Steps through the CLI (LC-018), not by two greps; Points 1 -> 2 |
