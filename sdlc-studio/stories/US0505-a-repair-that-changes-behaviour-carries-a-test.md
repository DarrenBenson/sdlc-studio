# US0505: A repair that changes behaviour carries a test asserting that behaviour, so a later silent revert reddens the suite

> **Status:** Review
> **Delivers:** CR0452
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/../reference-review.md, .claude/skills/sdlc-studio/scripts/critic.py, tools/tests/test_doc_claims.py
> **Epic:** EP0177
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** reviewer judging whether a repair will survive
**I want** every behaviour-changing repair to carry a test asserting that behaviour
**So that** a later silent revert reddens the suite instead of passing it, which is how one repair was lost entirely

## Acceptance Criteria

### AC1: a repair with no behavioural test is reported at review

- **Given** a repair changing behaviour with no test added
- **When** the review records its verdict
- **Then** the missing regression cover is reported as a finding, so an unpinned repair is visible before it is trusted
- **Verify:** pytest tools/tests/test_doc_claims.py::RepairCoverageTests::test_an_unpinned_repair_is_reported

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed |
