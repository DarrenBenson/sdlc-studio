# US1092: The retro's accuracy block and its VELOCITY row carry the priced cost per point under a named basis, and the forecast names every basis it pooled

> **Status:** Ready
> **Delivers:** CR0651
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_velocity_priced_basis.py, .claude/skills/sdlc-studio/reference-retro.md, changelog.d/US1092.md
> **Epic:** EP0292
> **Points:** 2
> **Depends on:** US1091
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, paying for every sprint the skill runs on her behalf
**I want** the retro's accuracy block to state each cost component and the priced total, the VELOCITY row to carry the priced cost per point under a Source naming its basis, and the forecast to say which bases it pooled
**So that** a rate pooled across the old and the new basis is never read as one figure

## Acceptance Criteria

- **AC1:** Given a fixture repository with an open run whose stamps carry priced figures, when `retro.py accuracy --id <retro> --tokens-from-harness --write` runs, then the retro's accuracy block states each component and the priced total on its own line, the VELOCITY.md row carries a priced-per-point figure and a Source naming the new basis (main thread and subagents, once per message), every earlier row keeps its cells, and `sprint.tokens_per_point(root)['basis']` names the set of Source bases among the rows the rate pooled
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_velocity_priced_basis.py::VelocityPricedBasisTests::test_accuracy_writes_components_priced_per_point_and_the_basis

## Notes

- Serves: Maya Okafor, End goal 3.
- AC1 must fail on: the row's Source left as `harness`, so two bases pool into one rate unnamed; an earlier row rewritten under the new definition; the components emitted only in JSON and never on the page
- Risk: The headline basis changes twice in one run (BG1111's de-duplication, then subagents). Rows on three bases would pool into one tokens-per-point rate unless the Source column tells them apart, which AC5 requires.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | sdlc-studio | Created via `new` (deterministic) |
