# US0643: A seat may sign only work it neither authored nor adversarially reviewed - three distinct contexts, enforced

> **Status:** Ready
> **Delivers:** CR0532
> **Created:** 2026-08-05
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/critic.py,.claude/skills/sdlc-studio/scripts/tests/test_sprint.py,.claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0209
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A seat may sign only work it neither authored nor adversarially reviewed - three distinct contexts, enforced
**So that** CR0532 is delivered by work that can be planned and checked

## Acceptance Criteria

> **Grooming note.** The enforcement this story's title names is already built: `record_signoff`
> refuses a principal equal to the author, refuses one drawn from `_session_reviewer_ids`, refuses
> a signing seat that is also an adversarial seat, and refuses a panel ratifying a verdict with no
> brief provenance. `persona_resolve.signoff_panel` assigns the two roles disjointly and
> `critic.py signoff --panel` reads the assignment from the run rather than the caller. What is
> missing is the wiring that makes any of it reachable: **nothing but a hand-run
> `persona_resolve.py panel --ceremony signoff` records the assignment**, so a run that forgets it
> cannot sign at all. That is LL0027, and it is this story's slice.

### AC1: opening a run records the sign-off panel

- **Given** a project whose policy is `review.signoff: panel`
- **When** `sprint plan --write` opens a run
- **Then** the run state carries the assignment - the adversarial seats and the disjoint signing seat - without any separate command being run
- **Mutant:** leave the assignment to the operator's memory - a run reaches its close and `signoff --panel` refuses for want of a record, which is today's behaviour
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SignoffPanelAssignmentTests::test_opening_a_run_records_the_signoff_panel
- **Verified:** yes (2026-08-05)

### AC2: a project on the operator policy is unchanged

- **Given** the shipped default `review.signoff: operator`
- **When** a run is opened
- **Then** no assignment is recorded and nothing about the plan's output moves, because a project that has not adopted panel sign-off must not acquire one
- **Mutant:** assign unconditionally - every consuming project silently gains a panel it never decided on
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SignoffPanelAssignmentTests::test_the_operator_policy_records_no_panel
- **Verified:** yes (2026-08-05)

### AC3: an unassignable panel refuses at plan time, not at close time

- **Given** a project whose seats cannot supply two disjoint roles
- **When** the run is opened under the panel policy
- **Then** the plan refuses and names the reason, because discovering it at the close strands a delivered run behind a sign-off nobody can give
- **Mutant:** swallow the resolution error and open the run anyway - the failure surfaces hours later at the gate that cannot be satisfied
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SignoffPanelAssignmentTests::test_an_unassignable_panel_refuses_at_plan_time_and_leaves_no_run
- **Verified:** yes (2026-08-05)

### AC4: the three refusals hold through the shipped CLI, not only in the library

- **Given** a unit with a recorded adversarial verdict
- **When** `critic.py signoff --panel` is driven for each of - the author signing, the adversarial seat signing, a signer other than the one the run assigned
- **Then** each is refused with its own message and no row is appended
- **Mutant:** call `record_signoff` directly instead of the verb - the assignment lookup is bypassed and every refusal that lives in the CLI path goes untested
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PanelSignoffCliTests::test_the_three_refusals_hold_through_the_shipped_verb
- **Verified:** yes (2026-08-05)

### AC5: the positive control - a correctly separated panel signs

- **Given** an assigned panel, a briefed adversarial verdict, and the assigned signer distinct from both author and reviewer
- **When** the same verb runs
- **Then** the sign-off is recorded and the unit's two-role gate is satisfied
- **Mutant:** refuse every panel sign-off - AC4 still passes for the wrong reason and only this criterion catches it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PanelSignoffCliTests::test_a_correctly_separated_panel_signs
- **Verified:** yes (2026-08-05)

### AC6: a panel cannot ratify a verdict with no brief provenance

- **Given** an assigned panel and an adversarial verdict carrying no brief fingerprint
- **When** the sign-off is attempted through the shipped verb
- **Then** it is refused, because a panel that ratifies an unprovable review LAUNDERS the missing provenance instead of catching it
- **Mutant:** drop the interlock - an unbriefed verdict is ratified. Found by mutation: the fixture supplied a brief in every other case, so no test reached this refusal
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PanelSignoffCliTests::test_a_panel_cannot_ratify_a_verdict_with_no_brief_provenance
- **Verified:** yes (2026-08-05)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Created via `new` (deterministic) |
