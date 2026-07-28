# US0538: Refine computes the seam map for a batch and reports a pair sharing a property with no criterion asserting it is preserved

> **Status:** Review
> **Delivers:** CR0468
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py
> **Epic:** EP0184
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** an operator planning a batch
**I want** refine to compute the seam map and report a pair sharing a property nothing preserves
**So that** two units that contradict each other are caught at plan rather than at review

## Acceptance Criteria

### AC1: the seam map is computed and reported at refine

- **Given** a batch containing two units that touch the same file, symbol or stated property
- **When** the batch is refined
- **Then** the seam map names that pair, and a pair sharing a property with no criterion asserting the property is preserved is reported at plan time
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::SeamMapTests::test_a_pair_sharing_a_property_with_no_preserving_criterion_is_reported
- **Verified:** yes (2026-07-28)

### AC2: the real contradicting pair from RUN-01KYKVZM is caught

- **Given** a fixture reproducing US0529 and US0530 - one unit fixing a property and its partner reintroducing it
- **When** the seam map is computed
- **Then** the pair is reported rather than passing, since both units individually satisfied their own criteria
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::SeamMapTests::test_the_us0529_us0530_shape_is_reported
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
