# US0643: A seat may sign only work it neither authored nor adversarially reviewed - three distinct contexts, enforced

> **Status:** Done
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
- **Verify:** manual - retired by US0919: the sign-off panel, its plan-time assignment and `critic.py signoff --panel` are retired
- **Verified:** manual (2026-09-25) - retired, superseded by US0919

### AC2: a project on the operator policy is unchanged

- **Given** the shipped default `review.signoff: operator`
- **When** a run is opened
- **Then** no assignment is recorded and nothing about the plan's output moves, because a project that has not adopted panel sign-off must not acquire one
- **Mutant:** assign unconditionally - every consuming project silently gains a panel it never decided on
- **Verify:** manual - retired by US0919: the sign-off panel, its plan-time assignment and `critic.py signoff --panel` are retired
- **Verified:** manual (2026-09-25) - retired, superseded by US0919

### AC3: an unassignable panel refuses at plan time, not at close time

- **Given** a project whose seats cannot supply two disjoint roles
- **When** the run is opened under the panel policy
- **Then** the plan refuses and names the reason, because discovering it at the close strands a delivered run behind a sign-off nobody can give
- **Mutant:** swallow the resolution error and open the run anyway - the failure surfaces hours later at the gate that cannot be satisfied
- **Verify:** manual - retired by US0919: the sign-off panel, its plan-time assignment and `critic.py signoff --panel` are retired
- **Verified:** manual (2026-09-25) - retired, superseded by US0919

### AC4: each refusal that the CLI can reach is refused for ITS OWN reason

> **RESTATED after an independent seat rejected the original.** It demanded that three
> refusals (the author signing, an adversarial seat signing, and a signer the run did not
> assign) each be reachable through the verb with its own message. Two cannot be told apart for
> any state the tooling produces: `signoff_panel(record=True)` always records a signer and
> always holds it DISJOINT from the adversarial seats, so an adversarial principal invariably
> trips the assigned-signer check first and returns its message. The test written to the
> original criterion asserted only a non-zero exit, which is why deleting the disjointness
> guard entirely passed 1,114 tests.
>
> **Narrowed after a second seat rejected the reason rather than the conclusion.** The first
> wording said the distinction was one "the design makes impossible". It is not: the
> assigned-signer check is guarded by `if signer and ...`, so a panel recorded with no signer
> would reach the disjointness refusal with its own message. No path in the shipped tooling
> records such a panel, so the conclusion stands and AC7 pins the guard where it IS reachable -
> but "impossible" claimed an invariant where there is a conditional, and a criterion restated
> in terms stronger than its evidence is the failure mode a restatement is most prone to.

- **Given** a unit with a recorded adversarial verdict and an assigned panel
- **When** `critic.py signoff --panel` is driven for the author signing, and for a signer the run did not assign
- **Then** each is refused with a message naming ITS OWN reason, and no row is appended
- **Mutant:** neuter either guard - the case that names it reddens, and only that case. A bare non-zero assertion cannot see the difference, which is the defect this restatement removes
- **Verify:** manual - retired by US0919: the sign-off panel, its plan-time assignment and `critic.py signoff --panel` are retired
- **Verified:** manual (2026-09-25) - retired, superseded by US0919

### AC5: the positive control - a correctly separated panel signs

- **Given** an assigned panel, a briefed adversarial verdict, and the assigned signer distinct from both author and reviewer
- **When** the same verb runs
- **Then** the sign-off is recorded and the unit's two-role gate is satisfied
- **Mutant:** refuse every panel sign-off - AC4 still passes for the wrong reason and only this criterion catches it
- **Verify:** manual - retired by US0919: the sign-off panel, its plan-time assignment and `critic.py signoff --panel` are retired
- **Verified:** manual (2026-09-25) - retired, superseded by US0919

### AC6: a panel cannot ratify a verdict with no brief provenance

- **Given** an assigned panel and an adversarial verdict carrying no brief fingerprint
- **When** the sign-off is attempted through the shipped verb
- **Then** it is refused, because a panel that ratifies an unprovable review LAUNDERS the missing provenance instead of catching it
- **Mutant:** drop the interlock - an unbriefed verdict is ratified. Found by mutation: the fixture supplied a brief in every other case, so no test reached this refusal
- **Verify:** manual - retired by US0919: the sign-off panel, its plan-time assignment and `critic.py signoff --panel` are retired
- **Verified:** manual (2026-09-25) - retired, superseded by US0919

### AC7: the disjointness guard is tested where it IS reachable (with AC4)

- **Given** a caller supplying its own panel, which is the path the guard backstops
- **When** the principal is one of the adversarial seats
- **Then** `record_signoff` refuses, naming the seat - with the positive control beside it, a disjoint principal on the identical call being accepted
- **Mutant:** delete the raise - this reddens and nothing else in the tree does
- **Verify:** manual - retired by US0919: the sign-off panel, its plan-time assignment and `critic.py signoff --panel` are retired
- **Verified:** manual (2026-09-25) - retired, superseded by US0919

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-06 | sdlc-studio | Second review round: US0640 Affects corrected to name config.py and triage_noise.py, where AC4 actually landed; US0643 AC4 restatement narrowed - the distinction is impossible for every state the tooling produces, not by design |
| 2026-09-25 | US0919 | AC1, AC2, AC3, AC4, AC5, AC6 and AC7 retired in the D0259 pattern: the sign-off panel, its plan-time assignment and `critic.py signoff --panel` are retired |
