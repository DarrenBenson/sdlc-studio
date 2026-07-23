# CR-0415: the delivery-mode disjointness check treats build tooling as an ordinary file, so a unit that restructures the pre-commit hook or the gate reads as file-disjoint from every other unit - yet every parallel agent commits through it

> **Status:** Proposed
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/reference-delivery.md
> **Priority:** Medium
> **Type:** Feature
> **Size:** S

## Summary

{{what changes and why}}

## Impact

{{who this affects and what breaks}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |

## Detail

Found fanning out Sprint 2. The delivery-mode offer correctly partitioned 29 units into 12
file-disjoint groups, and US0372 ("validate the commit-message rules ahead of the test lanes")
landed in a group of its own - because no other unit declares `.githooks/pre-commit` in its
`Affects`. By the analysis it is safely parallel with everything.

It is not. US0372 RESTRUCTURES the pre-commit hook, moving the expensive unit suites behind the
message check. Every other agent in the fan-out commits THROUGH that hook. Rebuilding it while
five agents are committing would change the gate under them mid-run - the one file that is an
implicit dependency of every unit in the batch, declared by none of them.

The same holds for `tools/skill-tests.sh`, `tools/test_noise.py`, the guards under `tools/`, and
`gate.py`: a unit that changes how the batch is VERIFIED is coupled to the whole batch, whatever
its `Affects` says. `Affects` describes what a unit edits, which is the right question for merge
conflicts and the wrong one for build-tooling.

I held US0372 back for serial delivery by hand rather than trust the offer here. That judgement
should not have to be remembered.

## Impact of the coupling

Any project using the parallel offer on a batch that includes its own tooling. The failure is not
a merge conflict - it is a gate changing underneath concurrent work, so the damage shows up as
unexplained lane failures in agents that did not touch anything related.

## Acceptance Criteria

- [ ] AC1: a unit touching build tooling is never offered as parallel-safe
- **Given** a batch holding a unit whose Affects names the pre-commit hook, the gate, or a guard under `tools/` that the commit path runs
- **When** the delivery mode is computed
- **Then** that unit couples to the whole batch rather than forming its own group, and the reason names build tooling rather than a shared file
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BuildToolingCouplingTests::test_a_gate_touching_unit_is_not_offered_parallel

- [ ] AC2: the set of build-tooling paths is declared, not inferred by name
- **Given** the check needs to know what counts as build tooling
- **Then** the paths are an explicit declared set the project can extend, so a new guard is added deliberately rather than being missed because its filename did not look like tooling
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BuildToolingCouplingTests::test_the_tooling_set_is_declared_and_extensible

- [ ] AC3: the contract is documented where the mode is documented
- **Given** a reader of reference-delivery.md
- **Then** it states that build tooling couples to the whole batch and why Affects is the wrong signal for it
- **Verify:** manual
