# US1020: The terminal transition names each criterion that passes without the change, even when the unit goes through

> **Status:** Draft
> **Delivers:** CR0616
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/reference-verify.md, .claude/skills/sdlc-studio/reference-schema.md, .claude/skills/sdlc-studio/scripts/tests/test_transition_revert_names_green.py, changelog.d/US1020.md
> **Epic:** EP0281
> **Points:** 3
> **Depends on:** US1018
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer who once found a criterion was green before the story existed, and only because I re-read it
**I want** the transition that closes a unit, including the sign, to name each criterion that still passes with the change reverted, and each declared exemption with its reason
**So that** a criterion that cannot tell done from not-done is visible when the unit closes, even when another criterion carries the unit through

## Acceptance Criteria

- **AC1:** Given a unit at In Progress with one criterion that goes red and one that stays green with its change reverted, when `transition.py set <id> Done --base <ref>` runs, then the unit reaches Done and the output names the green criterion, and not the red one, as passing without the change, with both remedies: re-author it, or declare it in `Revert-check-exempt` with a reason.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition_revert_names_green.py::RevertGateNamesGreenTests::test_only_the_criterion_green_without_the_change_is_named
- **AC2:** Given the same unit with its green criterion declared in a reasoned `Revert-check-exempt` field, when it moves to Done, then the output names that criterion as exempt, with its reason, and not as passing without the change.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition_revert_names_green.py::RevertGateNamesGreenTests::test_a_declared_exemption_is_shown_with_its_reason
- **AC3:** Given a run awaiting its signature whose batch holds a reviewed unit with one criterion that goes red and one that stays green with its change reverted, when `sprint.py sign` moves it to Done, then the sign's output names the green criterion as passing without the change.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition_revert_names_green.py::RevertGateNamesGreenTests::test_the_sign_names_the_green_criterion

## Notes

- Release: later (D0355 breakdown G7, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: print the green criteria only when the lane refuses the unit; or name every criterion the lane ran
- AC2 must fail on: drop exempt criteria from the transition's output, so a self-declared exemption is invisible at the terminal
- AC3 must fail on: put the per-criterion lines into `transition.py set`'s printing (`_print_result`) only, not into the transition's result, which the sign prints
- Probed at HEAD: on a unit with one criterion that reaches the change and one that greps text the base already held, `revert-check` printed AC2 green and passed the unit. The measurement CR0616 asks for already exists; nothing shows it at a gate.
- On the panel's RUN-01M40TSJ pass, this line would have named 5 criteria across 3 of the 15 units that passed.
- CR0616's example, US0188 AC1 in a consuming project, grepped a cron file whose header comments already named drift-check. Reverting that file leaves the grep green, so this line would have named the criterion.
- How CR0616's criteria map: (1) the baseline verb and its recorded result are replaced by this derived measurement. (2) Warn at Review/Done becomes a warning at the delivered terminal, the sign included, with no refusal mode. (3) `manual` criteria are already never run by revert_check, and `Revert-check-exempt` is the regression-guard marker; reference-schema.md's line on that field says so.
- The line is printed in both `report` and `block` modes. Under `off`, nothing runs and nothing is printed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G7 after the refine panel's review |
