# US0490: A charter carries its own goal review, and the run records who reviewed the goal and who ran it without refusing when they match

> **Status:** Ready
> **Delivers:** RFC0057
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/help/sprint.md
> **Epic:** EP0176
> **Points:** 3

## User Story

**As a** team where one person plans the sprints and another runs them
**I want** the charter to carry its own goal review, and the run to record who reviewed and who ran
**So that** the review travels with the work to whoever runs it, instead of dying in gitignored local state

## Acceptance Criteria

### AC1: the goal review travels with the charter

- **Given** a charter whose goal was reviewed by named seats
- **When** the charter is read by a different working copy
- **Then** the review is present on the charter, because it is committed with it rather than held in local state that does not travel
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CharterReviewTests::test_the_goal_review_travels_with_the_charter
- **Verified:** yes (2026-08-04)

### AC2: the run records the reviewer and the runner, and reports when they are the same

- **Given** a charter reviewed by one identity and run by the same identity
- **When** the run starts
- **Then** it proceeds, and records both identities and a plain statement that they matched - separation is recorded, never enforced
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CharterReviewTests::test_the_review_reaches_the_SHIPPED_ENTRY_POINT
- **Verified:** yes (2026-08-04)

### AC3: a charter whose goal was never reviewed is reported before it runs

- **Given** a charter carrying no goal review
- **When** the run starts
- **Then** the absence is reported plainly rather than being indistinguishable from a review that took place
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CharterReviewTests::test_an_unreviewed_goal_is_reported_not_silently_accepted
- **Verified:** yes (2026-08-04)

## Verification evidence

Functional. Three mutants executed, `__pycache__` purged and each child run under `python3 -B`,
anchors asserted unique, source restored byte-identical:

| Mutant | Result |
| --- | --- |
| stop reading the review from the charter | killed |
| drop the reviewer/runner comparison | killed |
| treat an absent review as reviewed | killed |

AC1's test proves the review TRAVELS by the only means that can: it records a review, then
deletes `sdlc-studio/.local` entirely and reads the verdicts back from the charter file alone.
A review held in local state passes every other assertion in the class and fails only that.

**Separation is recorded, never enforced**, and that is a decision rather than an omission. A
queue is often planned and run by the same person; refusing that would make the queue unusable
for the operator it was built for. What would be dishonest is leaving it unsaid, so a match is
stated plainly and travels with the run. A control asserts a different runner is NOT reported as
a match, so the statement discriminates.

An unreviewed goal is REPORTED rather than blocking, and its wording separates the two facts
that matter: never reviewed is different from a review that found nothing.

**The five obligations this repo attaches to a CLI verb were applied up front this time** rather
than discovered by refusal - documented as an invocation, a criterion naming the test that runs
the command, the ceremony declaration (already carried by `next`), an accurate `Affects`, and
nested `--root` defaulting to SUPPRESS.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed against the D0072 rulings |
