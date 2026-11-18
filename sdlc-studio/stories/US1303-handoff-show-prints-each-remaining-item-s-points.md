# US1303: `handoff show` prints each remaining item's Points and seat, and totals remaining points by suitability tag and by seat

> **Status:** Draft
> **Risk-class:** elevated
> **Delivers:** CR0733
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/help/handoff.md, .claude/skills/sdlc-studio/scripts/tests/test_handoff_effort.py, changelog.d/US1303.md
> **Epic:** EP0370
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** `handoff show` prints each remaining item's Points and seat, and totals remaining points by suitability tag and by seat
**So that** CR0733 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Each remaining item carries its points

- **Given** a batch with a remaining story of 3 points and a remaining bug with no Points line
- **When** `handoff.py show` is run, as text and with `--format json`
- **Then** the story's row shows 3 points and the bug's shows `unsized`, in both outputs. Fails on: an unsized unit printed as 0 points, or points in one output and not the other
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_handoff_effort.py::PointsTests::test_each_remaining_item_shows_its_points_or_unsized

### AC2: Each remaining item names one seat by the rule the help page states

- **Given** three remaining units: one held by an open decision, one whose verifier is failing or unproven, and one stalled before review
- **When** `handoff.py show` is run
- **Then** they name product, qa and engineering respectively, and `help/handoff.md` states the rule that maps a unit's state to its seat. Fails on: an item with no seat or two, or a seat the help page's rule does not give
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_handoff_effort.py::SeatTests::test_each_remaining_item_names_the_seat_its_state_needs

### AC3: Totals by tag and by seat re-add from the rows

- **Given** the three units above with known points
- **When** `handoff.py show` is run
- **Then** it ends with remaining points totalled by suitability tag and by seat, each total equal to the sum of its rows, and unsized items counted apart rather than as zero. Fails on: a total that differs from its rows, or unsized items folded into a total as zero
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_handoff_effort.py::TotalsTests::test_the_totals_re_add_from_the_rows

## Notes

- The handoff writers are retired (US0967); `show` is the read-only join that remains and is what this changes. The signed report's handed-over section is untouched.
- Affects corrected at grooming: the handoff's help page is `help/handoff.md`, not `help/sprint.md`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-17 | Claude Opus 5.5 (grooming) | Groomed: authored criteria with Verify lines, Affects corrected to the skill's test folder and this unit's fragment, notes |
