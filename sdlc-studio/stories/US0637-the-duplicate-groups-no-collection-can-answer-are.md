# US0637: The duplicate groups no collection can answer are derived from the resolver and named one by one

> **Status:** Ready
> **Delivers:** CR0445
> **Supersedes:** US0482
> **Created:** 2026-08-03
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Epic:** EP0174
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** reader of the duplicate-selector report deciding what is still owed
**I want** the groups the staleness sweep cannot answer named individually, with the verb that
makes them unanswerable
**So that** an exempt group is visible as an exemption rather than absorbed into a total

## Notes

Split from US0482, which was at the 8-point ceiling. This was that story's AC2, and it is the
only tooling change in the set - US0635 and US0636 are the burn-down itself, and neither
needs this to land first.

The set is unanswerable because the selector's verb sits outside `_COLLECTABLE`, so
`verify_ac.selector_resolves` answers `None` and the staleness sweep is blind to it (LL0047).
The failure mode this criterion exists to prevent is a number in prose: a count written at
grooming time is a fact about the day it was written, and a report that quotes it will keep
quoting it long after the set has changed.

## Acceptance Criteria

### AC1: the set is derived at lint time, never read from prose

- **Given** the duplicate groups whose selector `verify_ac.selector_resolves` answers `None`
  for
- **When** the lint runs
- **Then** the set is produced by calling the resolver on each group at lint time, so a group
  that becomes answerable - or stops being - moves in and out of it without anybody editing a
  document
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::UnanswerableGroupTests::test_the_set_is_derived_from_the_resolver_at_lint_time
- **Verified:** yes (2026-08-05)

### AC2: each member is reported individually, with its verb and its claimants

- **Given** the derived set
- **When** the report is printed
- **Then** each member appears on its own with the verb that makes it unanswerable and every
  AC claiming it, so the reader sees which groups are exempt rather than a count they cannot
  take apart
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::UnanswerableGroupTests::test_each_member_is_named_with_its_verb_and_claimants
- **Verified:** yes (2026-08-05)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-03 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-03 | Claude Opus 5 | Split from US0482 (8 points, over the ceiling): the reporting change that was that story's AC2 |
