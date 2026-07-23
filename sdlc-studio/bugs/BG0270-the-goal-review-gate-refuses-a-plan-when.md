# BG0270: The goal-review gate refuses a plan when a seat says NOT ONE INCREMENT, conflating a truthful themed-batch observation with a blocking objection

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Hit live opening Sprint 1 of the three-sprint run. `goal_review_status` builds its `objections` list from `verdict_polarity(achievable) == 'no' OR verdict_polarity(one_increment) == 'no'` (sprint.py ~1840), and the plan refuses on any objection unless overridden. All three seats judged the goal ACHIEVABLE (yes) and endorsed the batch, but all three also answered ONE INCREMENT = no, because it is a themed tooling-hardening batch of eight independent fixes - which is a truthful classification, not a rejection. The gate treated the three honest 'no's as blocking objections and refused the plan.

The conflation is the defect. `achievable = no` is a real objection: a seat saying the goal cannot be met should stop the plan (BG0262's whole point). `one_increment = no` is a DIFFERENT statement - it says the batch is not a single atomic increment, which is an INVEST ideal, not a gate. A themed batch (a tooling-hardening sprint, a bug-fix sweep, an audit-remediation batch) is a normal, valid sprint that legitimately is not one increment, and every seat here said so while endorsing the work. A gate that blocks it forces an override on every themed sprint, training the override the way BG0269's `SKIP_DIRS` trained --no-verify.

Note the shape: two distinct seat answers were folded into one blocking predicate. The fix is to separate them - an achievable-no blocks, a one-increment-no is surfaced as advice (the seats' framing: call it a themed batch), not a refusal.

## Steps to Reproduce

1. Record a goal review where every seat answers achievable=yes and `one_increment`=no (a themed batch all seats endorse). 2. Run `sprint plan --write`. Observed: the plan refuses, reporting the seats 'judged it NOT achievable', because `one_increment`=no was counted as an objection. Expected: the plan proceeds (all seats find it achievable); the `one_increment`=no is surfaced as an advisory note that the batch is themed, not a blocking objection requiring an override.

## Proposed Fix

Split the two answers in `goal_review_status`. Build `objections` from `achievable == 'no'` alone - that is the answer that means a seat thinks the goal cannot be met. Report `one_increment == 'no'` separately as an advisory (e.g. `themed_batch` or `not_atomic`), printed in the plan so the operator sees the seats' framing, but NOT added to the refusal set. A themed batch endorsed by every seat must plan without an override; reserve the override for a real achievable-no a human chooses to overrule.

## Second live occurrence (Sprint 2 opening, 2026-07-24)

Reproduced opening Sprint 2, in the ordinary course of work rather than a contrived fixture. All
three seats recorded `achievable = yes` and endorsed the batch; all three recorded
`one_increment = no`, each spelling out WHY it is not an objection ("a themed clearance batch of
independent fixes, which is the honest classification, not an objection"). The command replied:

    3 seat(s) judged it NOT achievable (product, engineering, qa)

That sentence is FALSE. No seat judged it unachievable; every one judged the opposite. So the
defect is not only that a themed batch is blocked - it is that the tool REPORTS the seats as
having said something they did not say, and that false sentence is what the operator reads when
deciding whether to override.

This raises the fix bar: separating the two answers must also correct the message, which today
names only achievability while being triggered by either field.

## Acceptance Criteria

### AC1: a one-increment `no` does not block a plan every seat finds achievable

- **Given** a goal review where every seat answers achievable=yes and one_increment=no (a themed batch the seats endorse)
- **When** `sprint plan --write` runs
- **Then** the plan proceeds without an override, because no seat objected to achievability
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ThemedBatchNotAnObjectionTests::test_one_increment_no_alone_does_not_refuse_the_plan

### AC2: an achievable `no` still blocks, unregressed

- **Given** a goal review where any seat answers achievable=no
- **When** `sprint plan --write` runs
- **Then** the plan is still refused and still requires a recorded override
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ThemedBatchNotAnObjectionTests::test_an_achievable_no_still_refuses

### AC3: the themed-batch observation is surfaced, not swallowed

- **Given** seats answering one_increment=no on an otherwise achievable goal
- **When** the plan renders its goal review
- **Then** it reports the batch as THEMED (not one atomic increment) as advice the operator can read, so separating the two answers loses no information
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ThemedBatchNotAnObjectionTests::test_the_themed_batch_note_is_reported

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Filed |

### AC4: the refusal never reports a verdict the seats did not give

- **Given** seats answering achievable=yes and one_increment=no
- **When** the goal review is recorded and rendered
- **Then** no output states that a seat judged the goal NOT achievable, because none did
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ThemedBatchNotAnObjectionTests::test_the_refusal_message_never_misreports_achievability
