# US0618: an unavoidable close-time repair is recorded as an explicit override with its reason

> **Status:** Ready
> **Delivers:** CR0527
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/close_owed.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py
> **Epic:** EP0204
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** an operator who had to fix something during a close
**I want** the exception recorded with its reason rather than absorbed silently
**So that** a rare necessity stays rare instead of becoming the routine the rule was written against

## Notes

Delivers criterion 4 of CR0527. US0616 refuses the inline repair and US0617 makes the residue
readable; this is the deliberate way through, for the case where deferring genuinely is not an
option - a defect that makes the close itself wrong, for instance.

The design constraint is that an override must cost something to use and must be countable
afterwards. A bare `--force` costs nothing and records nothing, and the close-owed ledger already
has the precedent: a bare `Velocity-override:` marker is not an override, only a reasoned one is.
Follow that.

## Acceptance Criteria

### AC1: an override requires a reason, and a bare flag is refused

- **Given** a close-time repair the operator judges unavoidable
- **When** the override is recorded without a reason
- **Then** it is refused, and with a reason it is accepted - the marker alone must not satisfy
  it, on the same terms `close_owed` already applies to a bare `Velocity-override:`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py::CloseRepairOverrideTests::test_a_bare_override_is_refused_and_a_reasoned_one_is_accepted

### AC2: the override names the unit it covers, and covers nothing else

- **Given** an override recorded for one unit
- **When** a second close-time repair appears
- **Then** the second is reported as uncovered - an override is per unit with its own reason, so
  one exception cannot silently license the next
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py::CloseRepairOverrideTests::test_an_override_covers_only_the_unit_it_names

### AC3: overrides are counted and surfaced, not merely stored

- **Given** a run carrying one or more recorded overrides
- **When** the close reports
- **Then** it states how many were used and with what reasons, so the exception is visible and
  countable rather than routine - an override nobody sees is indistinguishable from the inline
  repair the rule forbids
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py::CloseRepairOverrideTests::test_the_close_reports_the_override_count_and_reasons

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-03 | Claude Opus 5 | Groomed against CR0527 criterion 4; `Affects` widened to name the test module the fix lands in |
