# US0579: Every finding on a verdict is classified REGRESSION, NEW or PRE-EXISTING, and an unclassified verdict is refused

> **Status:** Review
> **Delivers:** CR0512
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0194
> **Points:** 5

## User Story

**As a** maintainer closing a batch
**I want** every finding sorted by whether this unit caused it
**So that** a defect is priced against the batch that introduced it

## Acceptance Criteria

> **Two axes, deliberately named apart.** `critic.py` already carries a `class` field with
> `FRESH` / `REPAIR_REGRESSION` / `UNCLASSIFIED`, which relates a round-N finding to round
> N-1's REPAIR, and `escalation_for` gates on it. This story adds a DIFFERENT question - does
> this finding predate the run's base ref - so it lands on a new field named `origin` carrying
> `regression` / `new` / `pre-existing`. The word "regression" appears on both axes and means
> different things: `REPAIR_REGRESSION` is "the repair broke it", `origin: regression` is "this
> unit's diff broke it". They are not merged, and the coverage gate reads `origin`. An
> independent engineering seat found this collision at goal review; without the separate name
> a second classifier would have been built on top of one CR0510 reports as effectively dead.

### AC1: every finding carries a classification

- **Given** a verdict whose findings are each marked on the `origin` axis as regression, new or pre-existing
- **When** it is recorded and read back
- **Then** each finding's `origin` survives the round trip, and the existing `class` axis is untouched by it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::FindingClassTests::test_a_classification_survives_the_round_trip
- **Verified:** yes (2026-08-01)

### AC2: an unclassified finding is refused

- **Given** a verdict carrying a finding with no classification
- **When** recording is attempted
- **Then** it exits non-zero naming that finding, because an unsorted finding is the one a close cannot price against the batch that caused it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::FindingClassTests::test_an_unclassified_finding_is_refused
- **Verified:** yes (2026-08-01)

### AC3: a verdict with no findings at all is still valid

- **Given** an APPROVE recording `none blocking`
- **When** it is recorded
- **Then** it succeeds, so the rule cannot be satisfied by refusing every clean pass
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::FindingClassTests::test_a_clean_pass_needs_no_classification
- **Verified:** yes (2026-08-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
