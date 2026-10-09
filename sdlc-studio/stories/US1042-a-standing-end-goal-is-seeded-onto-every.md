# US1042: A standing End goal is seeded onto every story minted to touch its files

> **Status:** Draft
> **Delivers:** CR0621
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/persona_goals.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/reference-persona.md, .claude/skills/sdlc-studio/scripts/tests/test_standing_goal_seed.py, changelog.d/US1042.md
> **Epic:** EP0285
> **Points:** 5
> **Depends on:** US1039, US1041, BG0995, US1025, US1026
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, whose product affects people who never use it
**I want** a story minted to touch a standing End goal's files to carry that goal as a criterion from the start
**So that** the plan advisory has nothing to name, because nobody had to remember to add the criterion

## Acceptance Criteria

- **AC1:** Given a Served card whose End goal 1 carries `Verify: shell true` and `Applies-to: ha/rooms/`, when `artifact.py new --type story --affects ha/rooms/bed.yaml` runs once with one `--ac`/`--verify` and once with none, then each story carries the goal as a criterion with the `standing:` marker and that Verify, rendered by artifact's own criteria writer after any supplied AC, `verify_ac.py run --story <it> --dry-run` reports it passed, and the story with no supplied AC keeps its scaffold and still counts ungroomed in `sprint.py plan`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_standing_goal_seed.py::ArtifactSeedTests::test_minted_story_touching_the_files_carries_the_goal
- **AC2:** Given stories minted with Affects `ha/rooms/upstairs/bed.yaml`, `other/ha/rooms/x.yaml`, `ha/rooms-old/x.yaml` and `HA/rooms/x.yaml`, when `sprint.py plan` runs over them, then it names none as owing, and the two it would not match carry no standing criterion.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_standing_goal_seed.py::AgreementTests::test_seed_and_plan_advisory_agree_on_every_path
- **AC3:** Given matching affects, when `refine.py apply` mints stories through the request seed carrying a criterion's own Verify line, through a breakdown entry supplying criteria, and as several stories under the ungroomed marker, then each story carries the standing criterion exactly once beside what that path wrote, and the marker-path stories still count ungroomed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_standing_goal_seed.py::RefineSeedTests::test_every_refine_path_keeps_one_standing_criterion
- **AC4:** Given a Negative persona card whose End goal (stated to exclude) carries Applies-to and Verify, when a story matching it is minted, then no criterion is seeded from it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_standing_goal_seed.py::ArtifactSeedTests::test_negative_persona_goal_is_never_seeded
- **AC5:** Given the Served card above, when `artifact.py new --type story --affects ha/rooms/bed.yaml --dry-run` runs, then the preview names the standing criterion it would seed and nothing is written.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_standing_goal_seed.py::ArtifactSeedTests::test_dry_run_names_the_criterion_it_would_seed

## Notes

- Release: later (D0355 breakdown G11, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: nothing is seeded, the criterion is prose with no Verify line, it is numbered over the supplied AC1, or it replaces the scaffold so a story whose only criterion is the standing one reads groomed
- AC2 must fail on: the seed matches with its own rule (fnmatch or a prefix) that disagrees with the plan advisory's, so the plan names a nested-path story the seed missed or the seed fills a near miss (LL0016)
- AC3 must fail on: refine's AC rewrite (refine.py:203, :241, or the breakdown path CR0628 adds) wipes the criterion, a path seeds it twice (once in artifact.new, again after the rewrite), or it makes an ungroomed story read groomed
- AC4 must fail on: seeding reads every card, including the persona the product declines to design for
- AC5 must fail on: the preview is silent about the criterion, so what a mint will add is visible only after it is written
- Serves: Maya Okafor #1.
- Later, for build risk rather than RFC0061 (panel): it joins the refine cluster. It is built after BG0995, G9's request-seed story and CR0628's breakdown story, and enters 6.2 only if all three land first.
- No third AC writer. G9 declined one renderer for the seed and `artifact.new` (G9.json out_of_scope: the seed's `### ACn:` blocks carry Given/When/Then lines the compact `- **ACn:**` shape cannot hold, and both are read by `verify_ac.parse_story`). So the standing goal is handed, as one more criterion with its Verify, to whichever existing writer renders that path's AC section: artifact's `_story_acs`, G9's Verify-carrying `_seed_acs`, or the same block writer beneath the ungroomed marker. It never picks a shape by inspecting the file.
- Moves `_component_names` into lib/sdlc_md.py, with sprint delegating, so the TRD constraints, the plan advisory and the seed share one matcher. sdlc_md is a hub: budget a 10-minute commit.
- Idempotent on the plan advisory's carrying predicate (marker or verbatim Verify).
- Stories only (panel, Q5): a bug's criteria are about its defect.
- G7: a standing criterion passes with or without the unit's change, so G7's terminal transition and lane return will name it on every story that carries one. The operator rules on exempting it (see questions); this story writes whatever that ruling requires.
- RFC0061 D6: if user personas learn from usage evidence, they would read the `standing:` marker this story writes; nothing here changes either way.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G11 after the refine panel's review |
