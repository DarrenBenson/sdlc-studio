# US0977: A lesson class finishes its lifecycle

> **Status:** Ready
> **Delivers:** CR0592
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lesson_lifecycle.py, changelog.d/US0977.md
> **Epic:** EP0270
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** a lesson class to move to `graduated` when its fix lands, and to retire when it has gone quiet, whichever clone recorded it
**So that** nobody hand-edits `lessons.jsonl` to finish a lifecycle the tool started

## Summary

Groomed under D0291 (sdlc-studio/reviews/backlog-sweep-2026-10-01.md) from CR0592 bullet 6 plus the graduation step the 2026-10-01 sweep had to do by hand (LC-002, LC-003, LC-006 and LC-008 were edited to `graduated`), 2 points.

- `lessons.close_pass` moves an `active` class to `graduating` and files its CR, but nothing moves a `graduating` class to `graduated` when that CR reaches a terminal status.
- `close_pass` retires a quiet class only when this clone's run archive knows its recording run and every hit run; a class recorded in another clone is known to neither and stays active for ever (LC-001 and LC-005 here).

Both are handled inside `close_pass`, which `sprint.py close` already runs; no new verb or ledger.

## Premise at HEAD

Executed at `85042135`: no code path writes the `graduated` state; the word appears only in the state vocabulary.

```text
$ grep -n '"graduated"' .claude/skills/sdlc-studio/scripts/lessons.py
1638:STATES = ("active", "graduating", "graduated", "retired")
```

## Acceptance Criteria

- [ ] **AC1** Given a fixture whose `lessons.jsonl` holds a `graduating` class whose `cr` names a CR at a terminal status, when `lessons.close_pass` runs (as `sprint.py close` runs it), then `lessons.py --root <fixture> classes` shows that class `graduated`, and a `graduating` class whose CR is still open is unchanged. Fails on: HEAD leaves both `graduating`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lesson_lifecycle.py::LessonLifecycleTests::test_a_class_graduates_when_its_cr_closes
- [ ] **AC2** Given an `active` class whose `recorded_run` and hit runs are absent from this clone's run archive, and no hit in the last `QUIET_RUNS` runs this clone knows, when `lessons.close_pass` runs, then the class is `retired`; a class with a hit in those runs stays `active`. Fails on: HEAD keeps the unknown-run class `active` because its recording run is in no known window
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lesson_lifecycle.py::LessonLifecycleTests::test_a_class_recorded_in_another_clone_retires_when_quiet

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-01 | engineering seat (groomer) | Groomed under D0291 (backlog sweep 2026-10-01): criteria authored, premise executed at HEAD 85042135, Points and Affects set |
