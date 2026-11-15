# US1159: An escape's root cause becomes a failure class that carries the files it applies to

> **Status:** Ready
> **Risk-class:** standard
> **Delivers:** CR0693
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/escape.py, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/templates/lessons-seed.jsonl, .claude/skills/sdlc-studio/scripts/tests/test_escape_class.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_confinement.py, changelog.d/US1159.md
> **Epic:** EP0309
> **Points:** 2
> **Depends on:** US1157
> **Persona:** Abena Osei

## User Story

**As a** head of engineering whose teams take changes through a change board
**I want** an escape's root cause becomes a failure class that carries the files it applies to
**So that** a defect that escapes to production is traced to where it got through, and the mistake is not repeated

## Acceptance Criteria

- **AC1:** Given a confirmed escaped bug BG0001 with a filled Root Cause and Affects `scripts/a.py`, when `escape.py to-class --bug BG0001 --class "a boundary never pinned" --rule ... --behaviour ...` runs, then `lessons.py class-add` (BG1268) is called and `sdlc-studio/lessons.jsonl` gains one row inject `build` and `review`, whose `evidence` cites BG0001 and the unit, and whose `files` holds the bug's Affects paths.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_escape_class.py::EscapeClassTests::test_a_root_cause_becomes_a_class_row_carrying_its_files
- **AC2:** Given a bug that is not escaped, one whose Root Cause is the scaffold, and a class name already in the store, when `escape.py to-class` runs, then each exits 2 naming its reason and the store is unchanged.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_escape_class.py::EscapeClassTests::test_an_unescaped_empty_or_duplicate_class_is_refused

## Notes

- Serves Abena Osei's End goal 4; delivers part of CR0693 (D0479).
- AC1 must fail on: a row written by hand-editing the store instead of class-add, or no files carried so nothing can be matched to a unit later
- AC2 must fail on: a class made from a bug with no root cause, or a duplicate row
- Start: lessons.py `find_class`/`next_class_id`/`_class_key` (:1937-1951), `load_store` and the new `class-add` verb (BG1268, landing in run 12: verify it is on main before building; if it is not, drop this story and pull US1063 in). The optional `files` field must be tolerated by lessons.py's reader and by `phase_digest`; test_lessons.py pins the store shape. Serves CR0693 AC4 (first half: the cause becomes a class).
- A new script or verb needs: a `sprint_report.NON_CEREMONY_VERBS` entry (or a close-checklist row), the regenerated `reference-scripts-surface.md`, a `### escape.py` catalogue heading, a root-census classification, a `build_parser`, and, for a script that writes files, the confinement allowlist (run twelve's lands were refused for each of these).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-14 | Claude Opus 5.5 (run thirteen grooming, D0479) | Groomed: criteria with Verify lines, must-fail notes, Affects with the tests each change exercises and this unit's fragment |
