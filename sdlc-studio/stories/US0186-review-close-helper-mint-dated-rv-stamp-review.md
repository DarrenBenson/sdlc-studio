# US0186: review close helper: mint dated RV, stamp review-state.json, derive LATEST.md, refuse anchor overwrite without a record

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/review_prep.py, .claude/skills/sdlc-studio/scripts/tests/test_review_prep.py, .claude/skills/sdlc-studio/reference-review.md
> **Epic:** EP0056
> **Points:** 5

## User Story

**As** Maya Okafor (solo founder-engineer, the Primary)
**I want** the review close to be one command: mint the dated RV, stamp review-state.json, derive LATEST.md
**So that** a review record can never again live only in the overwritable anchor, and the CRITICAL state stamp cannot be forgotten

## Acceptance Criteria

### AC1: Close subcommand stamps review-state.json

- **Given** a completed review with a dated RV file
- **When** review_prep.py close --rv RVxxxx runs
- **Then** per-leg last_reviewed/last_modified/review_findings_ref and the reviews.{id} entry are stamped deterministically
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_review_prep.py -k CloseStamp
- **Verified:** yes (2026-07-16)

### AC2: LATEST.md is derived, never orphaned

- **Given** a close whose dated RV file does not exist
- **When** the helper runs
- **Then** it refuses to touch LATEST.md - the anchor is derived from a record or not at all
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_review_prep.py -k AnchorRefus
- **Verified:** yes (2026-07-16)

### AC3: The workflow invokes the helper

- **Given** a reader of the review workflow
- **When** they reach step 4
- **Then** reference-review.md instructs the close subcommand instead of hand-steps
- **Verify:** grep "review_prep.py close" .claude/skills/sdlc-studio/reference-review.md
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
