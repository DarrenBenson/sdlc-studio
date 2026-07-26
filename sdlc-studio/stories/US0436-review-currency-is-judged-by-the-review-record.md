# US0436: review-currency is judged by the review record, not the anchor commit time, so a passed lane cannot be re-broken by a correct-content edit

> **Status:** Review
> **Delivers:** CR0421
> **Created:** 2026-07-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Epic:** EP0162
> **Points:** 3

## User Story

**As an** operator who has just re-run the review
**I want** the close's review-currency lane to judge the review RECORD, not the anchor file's commit time
**So that** a review that genuinely ran reads current - a byte-identical re-stamp is not called stale,
and no lane can be cleared only by a substantive edit to an artefact whose content is already correct

## Acceptance Criteria

### AC1: currency is read from the review record, not the anchor's commit time

- **Given** a review whose `.local/review-state.json` records a `last_reviewed` newer than every
  artefact, while `reviews/LATEST.md` carries an older commit time (a byte-identical re-stamp git saw
  no change in)
- **When** the `review-current` close lane evaluates
- **Then** it reads current from the review record and does not report the anchor as stale
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ReviewCurrencyByRecordTests::test_currency_is_judged_by_the_review_record
- **Verified:** yes (2026-07-26)

### AC2: the two currency checkers agree on identical state

- **Given** one review state
- **When** both the `review-current` lane and `review_prep`'s own staleness read it
- **Then** they return the same verdict - the close lane and the currency checker no longer give
  opposite answers on identical state
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ReviewCurrencyByRecordTests::test_the_lane_and_the_currency_checker_agree
- **Verified:** yes (2026-07-26)

### AC3: the invariant is stated in reference-sprint.md

- **Given** the shipped `reference-sprint.md`
- **When** it is read
- **Then** it states that a close never requires an edit that invalidates a lane it has already
  passed - currency is a property of the review record, not of a file's commit time
- **Verify:** grep "never requires an edit that invalidates a lane" .claude/skills/sdlc-studio/reference-sprint.md
- **Verified:** yes (2026-07-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Created via `new` (deterministic) |
