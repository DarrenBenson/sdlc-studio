# CR-0556: A bug reaches a terminal status with no independent judgement of its plan OR its code - the only gate is evidence it reports about itself

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/reference-doctrine.md
> **Evidence:** Dry-run through the shipped entry point across all 23 open bugs on 2026-08-25: 21 owe a test plan, 20 a Verification depth, 18 ticked criteria, 1 its mutants executed, 1 nothing - and 0 owe an independent review. `transition.py:961` for the story-only two-role gate; `transition.py:1047` and `_IMPL_TARGETS` for the entry gate a bug never reaches; `transition.py:921` and `_planned_mutant_gate` at `:1922` for what a bug does meet.
> **Date:** 2026-08-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Stories are held by two independent halves at Done - an adversarial pass recorded as evidence and a reviewer-of-record sign-off - plus a pre-code test-plan approval. A BUG is held by neither. `transition.py:961` gates the two-role review as `type_ == "story" and target_canon == "Done"`, and the entry `_test_plan_gate` never fires for a bug because `Fixed` is not in `_IMPL_TARGETS`. What remains is `_planned_mutant_gate` at the terminal transition, which asks for a `## Test Plan` whose mutants have been executed, and `_bug_depth_gate`, which asks for a parseable `Verification depth`. Both read evidence the AUTHOR produced about their own change. Measured across all 23 open bugs by dry-run: not one owes an independent review of any kind.

## Impact

Every project using the skill, and this one holds 610 bugs against 683 stories - so roughly half the delivered work in this repository has never been independently judged. The asymmetry is not a decision anybody recorded; it is what the gates happen to do. It matters most exactly when a backlog sweep is about to close many bugs at once on self-reported evidence, which is the situation here. Against it: a bug's executed mutants are stronger evidence than a review opinion, and adding ceremony to bugs is the opposite of what this project spent a week trying to reduce.

## Acceptance Criteria

- [ ] Given a bug reaching a terminal status under whichever option is adopted, when the gate runs, then the independent element it demands is stated in the refusal, so an author learns what is wanted rather than that something is missing
- [ ] Given a project that has not adopted the change, when a bug transitions, then behaviour is unchanged - bound behind a dated cutoff on the same terms as every sibling gate, so an existing backlog is not retro-refused
- [ ] Given the asymmetry between bugs and stories after this lands, when the doctrine is read, then it STATES which types are independently judged and at which transition, because the current asymmetry is undocumented and was found by measurement rather than by reading
- [ ] Given a bug whose declared mutant was killed by a test its criterion does not name, when the adopted check runs, then that is reported - the specific weakness this request is filed about, and the one a review found six instances of in a single six-unit batch

## Recommendation

Option 2, and NOT before the backlog sweep. The gate's weak point is precise: it takes the author's word that a declared mutant was executed and that it reaches the change - and RUN-01M0JD1W found six plan rows across three units whose declared mutant could not fail the test its own criterion named, found only because an independent seat compared the ledger's kill node to the criterion's Verify line. That check is narrow, mechanical and exactly what CR0554 would automate. Filing this now so the asymmetry is on record; acting on it now would make the sweep it endangers more expensive, which is the wrong order.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-25 | sdlc-studio | Raised |
