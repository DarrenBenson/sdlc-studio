# US0678: A unit whose diff cannot be resolved bands FULL and names the basis the estimate used

> **Status:** Blocked
> **Delivers:** CR0549
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/route.py, .claude/skills/sdlc-studio/scripts/tests/test_route.py
> **Epic:** EP0217
> **Blocked by:** D0150 and CR0555. A pre-code goal review REJECTED this batch three times. The third rejection was decisive: the measurement justifying the design was taken against a throwaway script rather than the weighted pipeline `route.estimate` actually runs, and three literal readings of the criterion through the real pipeline land at 81 to 97 per cent `light` - the mirror image of the defect, in the more dangerous direction. D0150 then ruled out the class entirely: no author-declared field may gate review depth, and `Points` is author-declared. CR0555 replaces the approach - the expensive half of the gate MOVES to the terminal transition where a diff exists, rather than being banded on a signal that must be read before one does. Do not build this batch; it is kept for its review record, which cost three rounds to produce. Disposition: basis naming - partly survives; the diff half may be reusable under CR0555.
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
| 2026-08-24 | sdlc-studio | RE-GROOMED against CR0549's second and third corrections after a pre-code goal review REJECTED the first attempt: the declared basis now reads `Points` and `Affects` breadth rather than whole-file complexity, measured to move `light` from 13% to 33%. |
