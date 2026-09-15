# US0626: an unfinished batch unit holds the close through its stop-ship step, naming where its findings went, while Review and rung-end units do not

> **Status:** Ready
> **Delivers:** CR0526
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0206
> **Points:** 5
> **Depends on:** US0625, US0627
> **Persona:** Maya Okafor

## User Story

**As a** operator closing a sprint
**I want** an unfinished batch unit to hold the close through its stop-ship step (D0193), naming the unit and where its findings went, while units at Review, Fixed or their rung's end do not
**So that** a run cannot be recorded as finished over work that never reached a terminal status

## Acceptance Criteria

### AC1: an unanswered unit holds the close through the stop-ship step, not a new gate (D0193)

- **Given** an open run whose batch holds a unit at In Progress with no ruling for it in the retro's Known issues carried table
- **When** `sprint.py close --dry-run` runs
- **Then** the stop-ship step (the known-issues checklist row) refuses, naming the unit and its status - and no new blocking step is added to the close chain
- **Mutant:** report the unit as an advisory - the close completes over unfinished work and the record claims a run that did not happen
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::UnansweredUnitHoldsTheCloseTests::test_an_in_progress_unit_holds_the_close_through_the_stop_ship_step

### AC2: Review, Fixed and rung-end units do not hold it - this sprint's own close completes

- **Given** a batch whose stories are at Review awaiting sign-off - one of them carrying a REJECT that `critic.coverage_state` reads as repaired (a complete repair, no re-review) - whose bugs are at Fixed, and a design-rung run whose units end at Ready
- **When** `sprint.py close` runs and then `close --apply-signoff`
- **Then** the stop-ship step does not refuse on any of them, and the apply-signoff path completes to an all-terminal batch - EXCEPT a unit, at any non-abandoned status, whose standing REJECT `critic.coverage_state` does not read as repaired and whose findings were not filed: that unit holds (D0196c). The repaired Review unit is the control that a reader of the standing verdict alone would fail - 87 repaired units in this repository still carry one
- **Mutant:** count Review as unanswered - every real close in this project deadlocks, because Review reaches Done only inside apply-signoff
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::UnansweredUnitHoldsTheCloseTests::test_review_fixed_and_rung_end_units_do_not_hold_the_close

### AC3: a ruling or a drop answers the unit; a stop-ship ruling holds

- **Given** the In Progress unit, ruled not-stop-ship or deferred in the carried table, or dropped with `sprint.py batch drop --reason`; and separately, ruled stop-ship
- **When** the close runs in each case
- **Then** the ruled-not-stop-ship, deferred and dropped cases no longer hold; the stop-ship case holds, naming the ruling
- **Mutant:** treat every ruling as an answer - a stop-ship ruling then releases the close it exists to hold
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::UnansweredUnitHoldsTheCloseTests::test_a_ruling_or_a_drop_answers_and_stop_ship_holds

### AC4: the refusal says where the unit's findings went

- **Given** an unanswered unit whose recorded REJECT findings were closed with `filed:` dispositions naming BG ids, and one with none filed
- **When** the close refuses
- **Then** the refusal names the filed ids for the first and says NONE filed for the second
- **Mutant:** print the unit id alone - the operator is told something is wrong and not what to read
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::UnansweredUnitHoldsTheCloseTests::test_the_refusal_names_where_the_findings_went

### AC5: one predicate: the close and `stop` agree on what is unanswered (L-0408)

- **Given** one fixture batch mixing In Progress; Review; a Review unit with an unanswered REJECT; a Review unit whose REJECT is completely repaired; a bug at Fixed with a REJECT recorded AFTER it reached Fixed; ruled; dropped; a unit parked by `sprint decision defer` with its decision pending and a unit whose `Depends on:` runs through it; a parked unit carrying an unrepaired REJECT; a unit whose REJECT has only SOME findings filed; plus a standing `rule:sprint-checklist:known-issues` waiver
- **When** the close's stop-ship step and `stop`'s refusal each name the unanswered set
- **Then** they name the same set, because both read one shared predicate whose REJECT half is `critic.coverage_state` and nothing else (L-0408): the parked unit and its dependant are answered (D0196a), the repaired Review unit is answered, the unanswered-REJECT Review unit, the bug rejected after Fixed, the REJECT-carrying parked unit (D0196c's exception list is complete, so the REJECT wins over the park) and the partly-filed unit (a REJECT is answered only when ALL its findings are closed, by repair or filing, as `critic.repair_state` reads them) are unanswered
- **Mutant:** give the close its own exemption list - the two readers disagree on a Review unit and the one that blocks is the one nobody tested
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::UnansweredUnitHoldsTheCloseTests::test_close_and_stop_name_the_same_unanswered_set

### AC6: a checklist waiver does not answer an unfinished unit (D0196b)

- **Given** the In Progress unit with no ruling, and a standing `rule:sprint-checklist:known-issues` waiver in the decisions log
- **When** the close runs
- **Then** the unit still holds the close - the waiver releases the checklist row's other states, never D0193's predicate, because a waiver never expires and would release the hold for every later run
- **Mutant:** let the waiver clear the row wholesale - one old ruling becomes a permanent exit from the stop-ship question
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::UnansweredUnitHoldsTheCloseTests::test_a_checklist_waiver_does_not_answer_an_unfinished_unit

### AC7: `stop`'s pending-decision exit stays - the paired control for D0196a

- **Given** a run whose every remaining unit is parked on a pending decision or depends on one
- **When** `sprint.py stop` runs
- **Then** it stops, as today, and it reaches that answer THROUGH the shared predicate rather than `stop`'s old reader - the existing UnblockedWorkBlocksTheStopTests::test_a_stop_is_allowed_when_no_unit_can_proceed stays green beside it as the regression net
- **Mutant:** count a parked unit (or its dependant) as unanswered - every pause for the operator's decision then needs --force
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::UnansweredUnitHoldsTheCloseTests::test_stop_still_exits_when_every_remaining_unit_is_parked_through_the_shared_predicate

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-15 | sdlc-studio | Retitled: was 'sprint close and sprint stop refuse while any batch unit is non-terminal, naming each and where its findings went' |
| 2026-09-15 | sprint planning 2026-09-15 | Re-groomed at the sprint goal review (round 1: all three seats refused a goal carrying CR0526) against D0193 (an unfinished unit feeds the close's stop-ship step, not a third gate) and D0194 (one stop-ship store, the retro's carried table). As first groomed it deadlocked every real close: Review is non-terminal and reaches Done only inside apply-signoff, after the chain closed the run. Now the hold runs through the stop-ship step, exempts Review, Fixed and rung-end units, and shares one predicate with stop; the other run-ending routes moved to US0823. |
| 2026-09-15 | sprint planning 2026-09-15 | Goal review round 2 repairs: AC2 no longer exempts a Review unit carrying an unanswered REJECT (D0195c); AC5's fixture adds a parked unit and a standing checklist waiver, the two shapes where close and stop would otherwise disagree; new AC6 - a checklist waiver does not answer an unfinished unit (D0195b). |
| 2026-09-15 | sprint planning 2026-09-15 | Goal review round 3 repairs (D0196 supersedes D0195): the REJECT half of the predicate is critic.coverage_state alone, at any non-abandoned status; AC2 and AC5 add the repaired-Review control and a bug rejected after Fixed; AC5 adds a dependant of the parked unit; new AC7 pins stop's pending-decision exit (a ruled control, green by design). |
| 2026-09-15 | sprint planning 2026-09-15 | Goal review round 4 notes (all three seats YES): AC5 adds a REJECT-carrying parked unit (D0196c's exception list is complete, so the REJECT wins) and a partly-filed REJECT (answered only when ALL findings are closed); AC7 names its own test through the shared predicate instead of borrowing US0299's verifier under another spelling (ruling withdrawn); depends on US0627, whose resolvable-id rule its repaired fixtures need. |
