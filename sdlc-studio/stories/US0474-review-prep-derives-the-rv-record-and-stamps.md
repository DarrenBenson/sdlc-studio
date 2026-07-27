# US0474: review_prep derives the RV record and stamps the covered units from one recorded sprint-review APPROVE, without touching operator prose

> **Status:** Ready
> **Delivers:** CR0424
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/review_prep.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_review_prep.py, changelog.d/{{US-id}}.md
> **Epic:** EP0171
> **Points:** 5

## User Story

**As a** agent closing a sprint whose adversarial review is already recorded
**I want** the RV record and the review stamp derived from that sprint-review row
**So that** one reviewer verdict is entered once instead of twice across two record surfaces

## Acceptance Criteria

### AC1: AC1: one APPROVE row covering the batch mints the RV and stamps exactly the units it covers

- **Given** a workspace with a single critic sprint-review APPROVE row covering every unit of the run's batch, no RV for it, and existing review-state.json stamps on the four doc legs
- **When** the derivation runs for that batch
- **Then** exactly one RV file exists under sdlc-studio/reviews/ with its index row, and review-state.json records `last_reviewed` and `review_findings_ref` = that RV id for EVERY covered unit key and for no other key - the prd/trd/tsd/personas entries keep their previous values byte-for-byte, because a full-diff code review is not a document review
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_prep.py::DeriveFromSprintReviewTests::test_an_approve_mints_the_rv_and_stamps_only_the_covered_units

### AC2: AC2: the derived record carries the review's content, not a placeholder scaffold

- **Given** a sprint-review row with a reviewer, an author, a base and findings text
- **When** the RV and the anchor citation are derived from it
- **Then** the RV body carries the reviewer, author, verdict, covered units and findings from the row, the anchor citation names the RV id, and no unsubstituted `{{placeholder}}` remains in either
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_prep.py::DeriveFromSprintReviewTests::test_the_derived_record_carries_the_review_content_not_a_placeholder

### AC3: AC3: partial coverage refuses, and so does a union of rows that jointly cover the batch

- **Given** a three-unit batch with (a) one APPROVE row covering two of the units, and separately (b) two APPROVE rows that jointly cover all three but neither covering all
- **When** the derivation runs against each
- **Then** both refuse non-zero naming the units the single row does not cover, mint no RV and leave review-state.json byte-identical - coverage is ONE row's judgement over one range, never a union, because `critic.sprint_review_for` resolves the latest row per unit and would otherwise let two half-batch reviews derive a record neither reviewer authorised
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_prep.py::DeriveFromSprintReviewTests::test_partial_coverage_and_a_two_row_union_both_refuse

### AC4: AC4: a REJECT row never derives a record

- **Given** a sprint-review row covering the whole batch whose verdict is REJECT
- **When** the derivation runs
- **Then** it refuses non-zero saying a rejected range is not an approval, and mints and stamps nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_prep.py::DeriveFromSprintReviewTests::test_a_reject_row_never_derives_a_record

### AC5: AC5: the anchor is written only inside the close-status block, so operator prose survives

- **Given** a sdlc-studio/reviews/LATEST.md whose narrative outside `<!-- close-status:begin -->`/`<!-- close-status:end -->` carries a unique operator sentence
- **When** the derivation cites the derived RV id in the anchor
- **Then** the RV id appears INSIDE the delimited block, every byte outside the block - including that operator sentence - is unchanged, and the whole-file `review_prep.close(latest_body=...)` path (an unconditional `atomic_write` of LATEST.md, review_prep.py:279) is not the path taken. LATEST.md is the orientation document AGENTS.md sends every fresh context to first, so a derivation that can clobber it is the more expensive failure than a review entered twice
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_prep.py::DeriveFromSprintReviewTests::test_operator_prose_outside_the_close_status_block_survives_byte_for_byte

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
