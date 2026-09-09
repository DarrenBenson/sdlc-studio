# EP0250: A test plan is checked for falsifiability, not only for shape

> **Status:** Draft
> **Derived Point Total:** 13
> **Parent:** CR0569
> **Created:** 2026-09-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0569. Delivers the work CR0569 requested.

## Story Breakdown

- [ ] [US0819: The plan probe runs each criterion against the tree and reports a pass as the finding](../stories/US0819-the-plan-probe-runs-each-criterion-against-the.md)
- [ ] [US0820: sprint plan refuses a batch carrying an unruled green or unknown criterion](../stories/US0820-sprint-plan-refuses-a-batch-carrying-an-unruled.md)

## Acceptance Criteria (Epic Level)

- [ ] Given a criterion whose `Verify:` selector PASSES against the tree as it stands, when `verify_ac.py testplan probe --unit <id>` runs, then that criterion is reported GREEN, the command exits non-zero, and the line names the unit and the criterion. A criterion the tree already satisfies is one whose delivery proves nothing
- [ ] Given a criterion whose selector selects NOTHING, when the probe runs, then it is reported `not-yet-written` and does not fail the command. That is the ordinary state before the test exists, and a check that refuses every plan at the moment plans are made is switched off rather than satisfied
- [ ] Given a criterion whose selector FAILS, when the probe runs, then it is reported `red` and the command exits 0. The paired control: a probe that reports every criterion as a finding satisfies the first row on its own
- [ ] Given a probe run whose answer cannot be trusted - the verifier times out, or its runner is absent - when the probe runs, then the criterion is reported `unknown` and fails the command rather than reading as green or as red. An unreadable bar is not a passed one, and a missing runner reading as `nothing to see` is the cheapest way for this gate to become useless
- [ ] Given a GREEN criterion carrying a recorded ruling that names it and its reason, when the probe runs, then it is reported `pinned` and does not fail the command; and given a ruling whose criterion text has since changed, that ruling no longer satisfies it. A regression pin deliberately fixes behaviour that already holds, and a ruling outliving the criterion it excused is an exemption nobody chose
- [ ] Given a batch under `sprint.py plan`, when any unit carries an unruled green or unknown criterion, then the plan is REFUSED naming the unit and the criterion. The library answer is the part a plan-time author never asks for; the wiring into the command people actually run is what makes it a gate rather than a habit
- [ ] Given a batch whose every criterion is red, not-yet-written or ruled, when `sprint.py plan` runs, then it proceeds. The paired control for the gate, because a gate that refuses every plan is removed rather than fixed

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-09 | sdlc-studio | Created via `new` (deterministic) |
