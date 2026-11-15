# US1157: A bug records that it escaped to production, the release it shipped in and the unit that let it through

> **Status:** Done
> **Risk-class:** standard
> **Delivers:** CR0693
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/help/bug.md, .claude/skills/sdlc-studio/reference-bug.md, .claude/skills/sdlc-studio/scripts/tests/test_bug_escape_fields.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_doc_coverage.py, changelog.d/US1157.md
> **Epic:** EP0309
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** head of engineering whose teams take changes through a change board
**I want** a bug records that it escaped to production, the release it shipped in and the unit that let it through
**So that** a defect that escapes to production is traced to where it got through, and the mistake is not repeated

## Acceptance Criteria

- **AC1:** Given a project with a tag v1.0.0, when `artifact.py new bug --escaped --shipped-in v1.0.0 --escaped-via US0001 ...` (and the same through `file_finding.py bug --escaped ...`) runs, then the bug header carries `Escaped: yes`, `Shipped-in: v1.0.0` and `Escaped-via: US0001`, and the Root Cause section is scaffolded in the body.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_bug_escape_fields.py::BugEscapeFieldTests::test_an_escaped_bug_carries_release_and_unit
  - **Verified:** yes (2026-11-15)
- **AC2:** Given `--escaped` with no `--shipped-in`, a `--shipped-in` naming no tag or release in the project, or an `--escaped-via` naming no unit on disk, when the command runs, then it exits 2 naming the missing or unresolved value and writes no file; a bug without `--escaped` is created exactly as before.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_bug_escape_fields.py::BugEscapeFieldTests::test_an_escape_without_a_resolvable_release_or_unit_is_refused
  - **Verified:** yes (2026-11-15)
- **AC3:** Given an escaped bug, when `transition.py` sets it Fixed, then it is refused until the Root Cause section holds text other than the scaffold.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_bug_escape_fields.py::BugEscapeFieldTests::test_an_escaped_bug_is_not_fixed_with_an_empty_root_cause
  - **Verified:** yes (2026-11-15)

## Notes

- Serves Abena Osei's End goal 4; delivers part of CR0693 (D0479).
- AC1 must fail on: the fields written only by one of the two creation paths, or no Root Cause scaffold
- AC2 must fail on: an escape recorded with an unresolved release or unit (a trace that points nowhere), or a normal bug changed
- AC3 must fail on: the Fixed transition ignoring an empty Root Cause on an escape
- Start: artifact.py bug body (~596-607, the `type_ == "bug"` branch), cmd_new flags (~1779-1810), file_finding.py --affects/--evidence (~2506-2513), transition.py _BUG_FIX_CLAIMS (:31). Header cells for a type come from `_header_cells` (artifact.py:906). Serves CR0693 AC1 (first clause); also Graham Doyle's End goal 3. No incident-issue work here (see deferred).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-14 | Claude Opus 5.5 (run thirteen grooming, D0479) | Groomed: criteria with Verify lines, must-fail notes, Affects with the tests each change exercises and this unit's fragment |
