# US0678: A unit whose diff cannot be resolved bands FULL and names the basis the estimate used

> **Status:** Draft
> **Delivers:** CR0549
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/route.py, .claude/skills/sdlc-studio/scripts/tests/test_route.py
> **Epic:** EP0217
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A unit whose diff cannot be resolved bands FULL and names the basis the estimate used
**So that** CR0549 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a DECLARED-basis estimate for a unit whose `Affects` cannot be read - absent, empty, or naming nothing that resolves - when it is scored, then it bands FULL and the dict says WHY, preserving the fail-towards-deeper-review rule at the layer that must still answer. This is the declared path only: a DIFF-basis request that does not resolve is refused rather than degraded, which US0684 owns
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::DiffScopedEstimateTests::test_an_unreadable_declared_surface_bands_full_and_says_why
- [ ] **AC2** Given any estimate that returns at all, when its dict is read, then it names its basis - `declared` or `diff` - so a reader can tell which question was answered. A band with no basis beside it cannot be interpreted, and interpreting one as the other is the conflation this epic exists to remove
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::DiffScopedEstimateTests::test_every_estimate_names_its_basis
- [ ] **AC3** Given a DIFF-basis estimate and a DECLARED-basis estimate of the SAME unit whose change is small against a large file, when both are taken, then they DIFFER - the paired control, because two bases that always agree are one basis with two names and the whole change would be inert
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::DiffScopedEstimateTests::test_the_two_bases_disagree_on_a_small_change_to_a_large_file

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
| 2026-08-21 | sdlc-studio | HELD - not in the RUN batch. CR0549's correction of 2026-08-21 applies: AC1 sends every unit with an unresolvable diff to FULL, which for a corpus of closed units is ALL of them - and that makes the band distribution narrower, contradicting US0680 AC2. The two were authored together and agree with each other rather than with the code. Re-groom before planning. |
