# US1041: Sprint plan names a batch story or bug that touches a standing End goal's files without carrying it

> **Status:** Draft
> **Delivers:** CR0621
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/persona_goals.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_plan_standing_owed.py, changelog.d/US1041.md
> **Epic:** EP0285
> **Points:** 3
> **Depends on:** US1039, US1040
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, approving a sprint plan
**I want** the plan and the goal review to name every batch story or bug that touches a standing End goal's files without carrying it
**So that** a change to a room cannot reach Done without a criterion saying the physical controls still work, however the unit was written

## Acceptance Criteria

- **AC1:** Given a batch story and a batch bug whose Affects fall under a standing End goal's `ha/rooms/` and whose criteria carry neither its `standing:` marker nor its Verify line verbatim, when `sprint.py plan --format json` runs, then `breakdown.standing_owed` names both units with the persona, the goal number and the matching path, the text plan prints a `standing criterion owed:` line for each, and the exit code and batch are unchanged.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_standing_owed.py::PlanStandingOwedTests::test_plan_names_a_story_and_a_bug_owing_a_standing_goal
- **AC2:** Given three matching stories, one whose Background quotes the goal text, one whose AC carries the `standing:` marker, and one whose reworded hand-written AC carries the goal's Verify line verbatim, when the plan runs, then only the first is named as owing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_standing_owed.py::PlanStandingOwedTests::test_carrying_is_the_marker_or_the_verbatim_verify_in_an_ac
- **AC3:** Given batch units touching `ha/rooms/upstairs/bed.yaml`, `other/ha/rooms/x.yaml`, `ha/rooms-old/x.yaml` and `HA/rooms/x.yaml` under `Applies-to: ha/rooms/`, when the plan runs, then the first two are named and the last two are not, as reference-persona.md states the dialect.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_standing_owed.py::DialectTests::test_applies_to_dialect_is_the_documented_whole_segment_rule
- **AC4:** Given the batch from the first criterion, when `sprint.py goal-review brief --brief-worklist` runs, then the brief lists the owed standing criteria the plan lists, and says none are owed when the batch owes none.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_standing_owed.py::BriefStandingOwedTests::test_brief_reads_the_plans_owed_list

## Notes

- Release: 6.2 (D0355 breakdown G11, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: no advisory is recorded, bugs are skipped, the wrong goal is named, or the advisory becomes a refusal (non-zero exit)
- AC2 must fail on: carrying is judged by a whole-file search, or by the marker alone, so a groomer who rewords the criterion is told it is owed
- AC3 must fail on: the advisory matches with a string prefix or fnmatch (which crosses `/` or folds case), or misses a nested directory
- AC4 must fail on: the brief derives its own list and disagrees with the plan, or prints nothing when none are owed, so an absence reads as unchecked
- Serves: Maya Okafor #1 (ship through a disciplined lifecycle, not ad-hoc edits).
- Decoupled from the seed (panel): it needs the Applies-to reader and a carrying rule, not the seeder. It matches with `_component_names` where it already lives in sprint (sprint.py:2677), so it touches no hub file.
- Carrying (panel, Q6): an AC block carrying the `standing: <Persona> #n` marker, or the goal's Verify line verbatim. One predicate in lib/persona_goals.py, which the later seed reuses for its idempotence.
- Derived in `breakdown` (sprint.py:2012) beside `affects_advisories`; `_compose_seat_brief` (sprint.py:11061) renders the plan's list rather than recomputing it.
- Names stories and bugs (panel, Q5): it is advice and reads Affects whatever the type. Seeding stays stories-only.
- Advice, never a refusal (LC-008).
- In the `_compose_seat_brief` cluster with BG1002, G10's CR0627 stories and the goal review story: built in sequence, never in parallel.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G11 after the refine panel's review |
