# BG0499: panel escalation reads a different ledger from the one review-batch writes, so two REJECT rounds through the CLI notify nobody

> **Status:** Closed
> **Severity:** High
> **Points:** 3
> **Verification depth:** functional
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Executed by the independent closing-review pass on US0603 during the RUN-01KYZKY5 close, reproduced through the shipped CLI in a fixture.
> **Created:** 2026-08-03
> **Created-by:** sdlc-studio file
> **Raised-by:** closing review RUN-01KYZKY5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`panel_escalation` is consulted only from `cmd_review_batch`, and it decides by calling `critic.unit_review_rounds`, which reads `sdlc-studio/reviews/critic-verdicts.md`. But `review-batch` records into `sdlc-studio/reviews/sprint-review-record.md`. So the two halves of the same command read and write different files: running `sprint review-batch --verdict REJECT` twice on one unit escalates nothing, and a panel that records two REJECTs through `critic.py record` and never runs `review-batch` also notifies nobody. The escalation fires only in the one combination where somebody uses both commands on the same unit.

## Steps to Reproduce

Run `sprint.py review-batch --units US0001 --verdict REJECT` twice against a fixture, then read stdout: no ESCALATED line appears. Record two REJECTs for the same unit with `critic.py record` instead, and no escalation appears either, because nothing calls `panel_escalation` on that path.

## Proposed Fix

Decide which ledger is the review record of a round, and make both halves use it. Then pin the wiring with a criterion that drives review-batch rather than calling `panel_escalation` directly - the round-two pass found that deleting the whole escalation loop leaves all five of US0603's criteria green.

## Acceptance Criteria

- [x] **AC1: two REJECT rounds escalate whichever command recorded them.**
  - **Given** a unit rejected twice - both rounds through `sprint review-batch`, both through
    `critic.py record`, or one through each
  - **When** the second is recorded
  - **Then** the operator is NOTIFIED, because a round is any recorded adversarial verdict
    naming the unit and the rule now reads both ledgers
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::EscalationReachesBothRecordingCommandsTests
  - **Verified:** yes (2026-08-03) - four tests, each driving a shipped `main([...])`

- [x] **AC2: one REJECT still does not escalate.**
  - **Given** a single rejection, which is the loop working rather than failing
  - **When** it is recorded
  - **Then** nothing escalates - a notification that fires on every ordinary finding is one the
    operator learns to ignore, which is the same outcome as not sending it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::EscalationReachesBothRecordingCommandsTests::test_one_reject_through_review_batch_does_not_escalate
  - **Verified:** yes (2026-08-03)

- [x] **AC3: deleting the escalation loop from either command reddens a criterion.**
  - **Given** the round-two finding that deleting the whole loop left all five of US0603's
    criteria green, because each called `panel_escalation` directly
  - **When** the loop is removed from `cmd_review_batch`, or from `critic.cmd_record`
  - **Then** a test fails in each case
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::EscalationReachesBothRecordingCommandsTests::test_two_rejects_through_critic_record_escalate
  - **Verified:** yes (2026-08-03) - both deletions executed as mutants and killed

## Verification evidence

Functional. Every criterion drives a shipped `main([...])` rather than calling the rule, which
is the distinction that let this survive: five criteria on US0603 called `panel_escalation`
directly and stayed green while nothing wired it to the ledger the command writes.

| Mutant | Result |
| --- | --- |
| escalation reads `unit_review_rounds` alone - the shipped defect | killed by 2 |
| drop the escalation loop from `critic.cmd_record` | killed by 1 |
| drop the escalation loop from `cmd_review_batch` | killed by 2 |

**The decision this bug asked for.** A round is any recorded adversarial verdict naming the unit,
from either ledger, and `critic.review_rounds_across_ledgers` is the one reader. It is
deliberately NOT folded into `unit_review_rounds`, which feeds `seat_verdicts` and the coverage
predicate: those ask which seat holds what verdict on one unit, and a batch row cannot answer
that - the reviewer reviewed a span, not a seat's slice. Two questions, two readers, with the
difference recorded beside both. `panel_escalation` moved to `critic.py` next to the ledgers it
judges; `sprint.panel_escalation` remains as a delegation, because one rule with two homes is
the shape that produced this defect.

## Round 2: what the independent review rejected, and what changed

REJECTed at the lane boundary with two blocking findings.

**There was a THIRD recording command.** `critic.py sprint-review` writes the same batch ledger
`sprint review-batch` writes, and the first repair left it unwired - so two REJECTs recorded
through it printed nothing, and the notice then surfaced later attached to an unrelated APPROVE
recorded through a different command. That is precisely the "fires only in one combination"
defect this bug exists to remove, surviving in the third door. Worse, the repair's own prose
asserted the opposite in two places - the changelog said "both recording commands" and the
function's docstring said "the two commands that record a round" - so the diff shipped a claim
the code contradicted. Both are corrected and the third command is wired.

**Two predicates had ZERO cover.** The reviewer mutated `if want in named:` to `if True:` and
the whole of `test_sprint`, `test_critic` and `test_conformance` stayed green - that predicate
is the only thing stopping a batch row naming one unit from escalating a different one. The
phase guard was equally unpinned. Behaviour was correct in both cases; the regression cover was
absent, which is the state where a later edit reverts it with the suite green.

Also repaired from the non-blocking set: a REFUSED `record` printed "Nothing was written" and an
ESCALATED line in the same breath, because the loop ran regardless of the exit code. It now runs
only when a round was actually written - noise on this channel is what makes an operator stop
reading it, which is the same argument AC2 makes for not escalating a first rejection.

Round-2 mutants, all killed: the unit-matching predicate, the phase guard, escalating on a
refused record, and dropping the escalation from `cmd_sprint_review`.

Two findings recorded and NOT fixed here. The split-panel branch is unreachable from a
batch-only history, because `escalation_notice` pairs a two-ledger round list with a one-ledger
`seat_verdicts` - pre-existing and outside this unit's criteria. And a mis-recorded batch REJECT
has no supersession path, so it is a permanent escalation trigger; that is a real gap in the
batch ledger's erratum story rather than in this rule, and it is left for a filing rather than
widened into here.

## Impact

The escalation exists so a twice-rejected or split-panel unit reaches the operator. On the path a user is most likely to take, it is silent.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-03 | closing review RUN-01KYZKY5 | Filed |
