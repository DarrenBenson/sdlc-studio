# US1045: Review prep reports which End goals each persona's stories serve

> **Status:** Draft
> **Delivers:** CR0623
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/review_prep.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/scripts/tests/test_review_prep_goals_served.py, changelog.d/US1045.md
> **Epic:** EP0285
> **Points:** 2
> **Depends on:** US1043, BG0966
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, running the unified review
**I want** the review's persona usage to say which End goals each persona's stories serve
**So that** a persona named only in a copied boilerplate block reads as serving no goal, rather than as used

## Acceptance Criteria

- **AC1:** Given two stories tagged `Serves: Maya Okafor #2` and a Jonah card that one story names only in a `### Persona Reference` block, when `review_prep.py prep --format json` runs, then `persona_usage.goals_served` maps Maya's End goal 2 to two stories and `no_goal_served` lists Jonah.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_prep_goals_served.py::GoalsServedTests::test_json_maps_personas_to_goals_their_stories_serve
- **AC2:** Given the same fixture, when `review_prep.py prep` runs as text, then the personas line names the personas whose stories serve no End goal, beside the defined and unused counts.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_prep_goals_served.py::GoalsServedTests::test_text_names_personas_serving_no_goal

## Notes

- Release: 6.2 (D0355 breakdown G11, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: goals served are counted from persona-name mentions rather than goal references, so the boilerplate block counts Jonah as serving
- AC2 must fail on: the JSON carries the field but the text render the Persona leg reads does not
- Serves: Maya Okafor #2 (know the true state of the work).
- Adds a dimension; does not redefine `unused` (panel agreed). The CR's 'counted as used only through a named goal' would report a persona linked from 24 stories as unused, the inverse of BG0966 and against its AC1.
- Build after BG0966, which rewrites the same `persona_usage` (review_prep.py:124) to read stories, CRs and epics.
- RFC0061 D4 and D6: one input of the 'served-goal outcomes' usage evidence workstream 4 names. Outcomes beside tag counts would be an addition, not a reason to wait.
- Test on a fixture: `review_prep.py prep` on this repo ran past a two-minute timeout in the probe.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G11 after the refine panel's review |
