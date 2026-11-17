# US1217: Critic record accepts a round two verdict from a fresh reviewer and records it under its own name

> **Status:** Won't Implement
> **Risk-class:** standard
> **Delivers:** CR0680
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/lib/cost_anatomy.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py
> **Epic:** EP0332
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Critic record accepts a round two verdict from a fresh reviewer and records it under its own name
**So that** CR0680 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A round two verdict from a fresh reviewer is recorded under its own name

- **Given** a unit with a round one REJECT from one reviewer
- **When** `critic.py record` records a round two APPROVE from a different reviewer who is not the unit's author
- **Then** the row is written under the fresh reviewer's name, the round one row is unchanged, and the unit's REJECT reads as answered so the Done gate no longer refuses on it. Fails on: the record refused because round two must come from the round one reviewer, or the row written under the round one reviewer's name
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::FreshRoundTwoReviewerTests::test_a_round_two_verdict_from_a_fresh_reviewer_is_recorded_under_its_name

### AC2: Independence and the round cap still hold for a fresh reviewer

- **Given** the same unit, and a second unit already at the review cap
- **When** `critic.py record` is given a round two APPROVE whose reviewer is the unit's author, and a further verdict from a fresh reviewer on the unit at the cap
- **Then** the first is recorded as a self-review that does not clear the Done gate, and the second is refused naming the cap; beside them a round two from the round one reviewer is recorded as it is today. Fails on: an author approving its own repair through the relaxed rule, or a round past the cap
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::FreshRoundTwoReviewerTests::test_the_author_and_the_cap_are_still_refused

### AC3: The cost anatomy attributes the round two transcript to the fresh reviewer

- **Given** a run whose unit has a round one verdict from one agent and a round two verdict from another, each with its own transcript
- **When** the cost anatomy is read for the run
- **Then** both agents are counted as reviewers and the round two transcript's cost is under the fresh reviewer's agent. Fails on: the round two transcript counted as other, or added to the round one reviewer
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py::CostAnatomyTests::test_a_fresh_round_two_reviewer_is_attributed_its_own_transcript

### AC4: The runbook no longer says a different reviewer's APPROVE cannot answer a REJECT

- **Given** the row of reference-sprint-toolchain.md on answering a REJECT
- **When** it is read
- **Then** it says round two may come from the rejecting reviewer or from a fresh reviewer who is not the author, each recorded under its own name. Fails on: the row still listing a different reviewer's APPROVE among the things that do not answer a REJECT
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::FreshRoundTwoReviewerTests::test_the_runbook_names_a_fresh_round_two_reviewer

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
