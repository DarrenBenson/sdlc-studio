# US1044: artifact new writes a story's Serves line from --serves

> **Status:** Draft
> **Delivers:** CR0623
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/reference-scripts-create.md, .claude/skills/sdlc-studio/scripts/tests/test_artifact_serves_flag.py, changelog.d/US1044.md
> **Epic:** EP0285
> **Points:** 2
> **Depends on:** US1043
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, whose stories are mostly minted by the tooling
**I want** `artifact.py new --serves "Maya Okafor #2"` to write the story's Serves line
**So that** a tooled story can name its End goal at mint without a hand edit the tooling cannot see

## Acceptance Criteria

- **AC1:** Given a project whose Maya card lists End goal 2, when `artifact.py new --type story --serves "Maya Okafor #2"` runs, then the story carries `> **Serves:** Maya Okafor #2` and `validate.py serves` reports no warning for it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact_serves_flag.py::ArtifactServesTests::test_serves_flag_writes_a_line_validate_accepts
- **AC2:** Given `--serves "Maya Okafor #9"`, when `artifact.py new --type story` runs with `--strict`, then nothing is minted and the refusal names the End goals the card has, and without `--strict` the story is minted and a warning names the same.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact_serves_flag.py::ArtifactServesTests::test_unknown_goal_refused_under_strict_warned_otherwise

## Notes

- Release: 6.2 (D0355 breakdown G11, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the flag is parsed and never written (a dead flag), or written in a form `check_serves` rejects
- AC2 must fail on: an unknown goal is accepted silently under `--strict`, or the refusal fires after an id is allocated
- Serves: Maya Okafor #1.
- The Serves goal reference story adds a reader; this is its tooled writer ('for every reader you add, name its writer'). No `artifact.py new` template writes the `Serves:` header today (panel probe).
- Resolved through the Serves resolver before an id is allocated, where `_resolve_persona` refuses (artifact.py:1140). A `serves` key in `--fields-file` works the same way.
- A per-story `serves` key in `refine.py apply`'s breakdown is CR0628's to decide, not this story's (panel, Q9).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G11 after the refine panel's review |
