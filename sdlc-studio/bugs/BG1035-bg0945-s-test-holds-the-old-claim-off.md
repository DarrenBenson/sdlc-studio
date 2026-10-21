# BG1035: BG0945's test holds the old claim off by one literal phrase, and the untracked first-ruling branch is unstated and unpinned

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_bg0940_fragment_matches_sign.py, changelog.d/BG0940.md, changelog.d/BG1035.md
> **Created:** 2026-10-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (triage); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-13T10:30:13Z

## Summary

From BG0945's round-1 QA review on 2026-10-13 (APPROVE, nothing blocking). (1) `test_bg0940_fragment_matches_sign.py` rules out the old wording with one literal `assertNotIn`: rewording the first sentence to 'so the filed page still checks VALID once it is signed' keeps the test green. (2) The note's 'Because the log is a tracked file' is true only when the decisions log existed and was committed before the close: in a project with no decisions.md at close, the late ruling creates it untracked, sign's tree check exempts an added untracked file, and `sprint sign` seals. The test sets up the tracked case on purpose; the untracked branch is neither stated nor pinned.

## Steps to Reproduce

Reword the note's first sentence as above and run the test (green). Run the BG0945 steps on a fixture with no decisions.md before the close: sign seals.

## Proposed Fix

Judge the note's claim about signing by meaning (no sentence says the page is signed after a late ruling), and either state the untracked first-ruling case in the note or pin it, deciding whether sign should seal there.

## Acceptance Criteria

- [ ] **AC1** Given a project whose decisions log does not exist at the close, when a late ruling is logged and `sprint sign` runs, then sign seals and the filed page still checks VALID
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_bg0940_fragment_matches_sign.py::FragmentMatchesSignTests::test_a_first_ruling_that_creates_the_log

## Impact

A release note can drift back to over-claiming with the test green, and a project's first late ruling is sealed over without the note saying so.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-13 | Claude Opus 5.5 (triage) | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
