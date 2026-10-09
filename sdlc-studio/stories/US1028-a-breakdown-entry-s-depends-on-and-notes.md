# US1028: A breakdown entry's depends_on and notes land on the story refine mints

> **Status:** Draft
> **Delivers:** CR0628
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/tests/test_refine_breakdown_dependencies.py, .claude/skills/sdlc-studio/help/refine.md, changelog.d/US1028.md
> **Epic:** EP0283
> **Points:** 2
> **Depends on:** US1026
> **Persona:** Maya Okafor

## User Story

**As** the operator ordering a reviewed breakdown's stories
**I want** each entry's `depends_on` written as the story's Depends on ids and its notes kept on the story
**So that** the planner sees the order the breakdown declared, and the design notes reviewed with it survive minting

## Acceptance Criteria

- **AC1:** Given entries whose `depends_on` name another entry of the breakdown by title, a story already on disk by its exact title, and an existing bug by id, when `refine.py apply --breakdown` runs, then each story's `> **Depends on:**` line lists the resolved ids, and `sprint.py`'s dependency reader returns them as edges.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine_breakdown_dependencies.py::BreakdownDependencyTests::test_depends_on_titles_and_ids_become_dependency_edges
- **AC2:** Given a `depends_on` entry that names neither an entry of the breakdown, nor a story title on disk, nor an artefact id, when refine runs, then it refuses before anything is minted, naming the story and the entry.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine_breakdown_dependencies.py::BreakdownDependencyTests::test_an_unresolvable_dependency_is_refused_before_minting
- **AC3:** Given an entry's `notes` naming identifiers such as `_seed_acs`, when the story is minted, then they appear verbatim as bullets under a `## Notes` section before the Revision History.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine_breakdown_dependencies.py::BreakdownDependencyTests::test_notes_are_kept_verbatim_under_their_own_heading

## Notes

- Release: 6.2 (D0355 breakdown G9, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the titles written as given, where `sprint._dep_ids` stops at the first non-id token (sprint.py:877-892), so no edge is read
- AC2 must fail on: resolving after minting and dropping whatever does not resolve
- AC3 must fail on: notes passed through the filer's markdown-safing, which rewrites identifiers the author already quoted, or dropped
- `artifact.py new` takes neither key (`FIELDS_FILE_KEYS`, artifact.py:1519-1526). The panel asked whether refine takes keys the story writer lacks. Decided: yes, refine owns these two. They only make sense across a breakdown (a title resolves against its sibling entries), and the Depends on line is written after all entries are minted, through `sdlc_md.insert_after_status`, the writer refine already uses for `Delivers:`. Moving them into `artifact.py new` is a later request if hand-minted stories need them.
- The field is `Depends on`, the spelling `sprint.py` reads (sprint.py:1050, :3244). Ids are resolved before minting, so an unresolvable entry refuses with nothing written. A title that matches two stories on disk refuses too, naming both.
- This is how cross-epic order in the D0355 drafts (titles of other groups' stories, bug ids) becomes Depends on ids at minting, instead of a hand edit afterwards.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G9 after the refine panel's review |
