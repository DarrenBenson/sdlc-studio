# CR-0569: A test plan is checked for shape but never for falsifiability, so a criterion already satisfied at HEAD passes every guard the toolchain has

> **Status:** Complete
> **Decomposed-into:** EP0250, EP0251
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Date:** 2026-09-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Three guards read a test plan before any code is written. `verify_ac lint` checks the Verify selectors' spelling, `testplan derive` checks each mutant carries an edit verb, names a path in the unit's Affects and does not restate its own criterion, and `batch_plan_shape check` checks the table's shape. Not one of them asks the question the plan exists to answer: CAN THIS CRITERION FAIL? A criterion whose behaviour the tree already has passes every one of them, and then passes at delivery too, because it was green before the work started. It costs a unit's whole cycle to discover that the work proved nothing.

Measured on RUN-01M20RWX, where sixteen units went to independent plan-review seats before any code: round one returned 113 findings on 14 units, 44 of them blocking, and the single largest category was criteria already true at HEAD. The seats found them by EXECUTION - running the criterion's own selector and reading the result. Nothing in the toolchain does that, so the check exists only in a reviewer's discipline, which is the shape LL0027 names as the weak one.

The machinery is already here. `verify_ac run` executes a criterion's selector, and its result carries `vacuous` - a run that exited clean having run no tests at all, decided per runner family. Those two facts separate the three states this check needs: a selector that selects nothing is the ORDINARY state before the test is written and is not a finding; a selector that fails is the state a plan-time criterion should be in; and a selector that PASSES is the finding. What is missing is the verb that says so and the wiring that runs it where plans are made.

## Impact

Every consuming project gets the check, not just this one. The failure it catches is expensive everywhere and invisible by construction: a criterion that was already true produces a green delivery, a passing review and a unit that changed nothing, and the only way it is currently caught is a reviewer choosing to run the selector by hand. On this run that discipline found the largest single category of plan defect across sixteen units.

## Acceptance Criteria

- [ ] Given a criterion whose `Verify:` selector PASSES against the tree as it stands, when `verify_ac.py testplan probe --unit <id>` runs, then that criterion is reported GREEN, the command exits non-zero, and the line names the unit and the criterion. A criterion the tree already satisfies is one whose delivery proves nothing
- [ ] Given a criterion whose selector selects NOTHING, when the probe runs, then it is reported `not-yet-written` and does not fail the command. That is the ordinary state before the test exists, and a check that refuses every plan at the moment plans are made is switched off rather than satisfied
- [ ] Given a criterion whose selector FAILS, when the probe runs, then it is reported `red` and the command exits 0. The paired control: a probe that reports every criterion as a finding satisfies the first row on its own
- [ ] Given a probe run whose answer cannot be trusted - the verifier times out, or its runner is absent - when the probe runs, then the criterion is reported `unknown` and fails the command rather than reading as green or as red. An unreadable bar is not a passed one, and a missing runner reading as `nothing to see` is the cheapest way for this gate to become useless
- [ ] Given a GREEN criterion carrying a recorded ruling that names it and its reason, when the probe runs, then it is reported `pinned` and does not fail the command; and given a ruling whose criterion text has since changed, that ruling no longer satisfies it. A regression pin deliberately fixes behaviour that already holds, and a ruling outliving the criterion it excused is an exemption nobody chose
- [ ] Given a batch under `sprint.py plan`, when any unit carries an unruled green or unknown criterion, then the plan is REFUSED naming the unit and the criterion. The library answer is the part a plan-time author never asks for; the wiring into the command people actually run is what makes it a gate rather than a habit
- [ ] Given a batch whose every criterion is red, not-yet-written or ruled, when `sprint.py plan` runs, then it proceeds. The paired control for the gate, because a gate that refuses every plan is removed rather than fixed

## Recommendation

Add `verify_ac.py testplan probe`, which runs each criterion's own Verify selector against the tree as it stands and classifies the result: `red` (the state a plan-time criterion should be in), `not-yet-written` (the selector selects nothing - ordinary before the test exists, and never a finding), and `GREEN` (the criterion is already satisfied, so delivering it would prove nothing). Manual and unspecified verifiers are named and skipped rather than guessed at.

A green criterion is sometimes legitimate - a REGRESSION PIN deliberately fixes behaviour that already holds, so it cannot silently rot. That case is declared rather than assumed, on the same pattern `verify_ac coverage rule` already uses for a line that cannot be covered: a ruling names the criterion and the reason and is hashed against the criterion's own text, so it cannot outlive the criterion it excused. An unruled green criterion is the finding.

Wire it into `sprint plan` over the batch, refusing before a run opens. That is the command run at plan time, and a check that only runs when somebody remembers is the rule this repository keeps re-learning it does not have.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-09 | sdlc-studio | Raised |
