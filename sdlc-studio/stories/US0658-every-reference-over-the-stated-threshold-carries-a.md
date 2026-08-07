# US0658: Every reference over the stated threshold carries a Reading Guide with an anchor and a line span

> **Status:** Ready
> **Delivers:** CR0538
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/docgen.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-decisions.md, tools/check_budgets.py, .claude/skills/sdlc-studio/scripts/tests/test_docgen.py, tools/tests/test_check_budgets.py
> **Epic:** EP0211
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** Every reference over the stated threshold carries a Reading Guide with an anchor and a line span
**So that** CR0538 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: every reference over the threshold carries a GENERATED Reading Guide

- **Given** the 27 `reference-*.md` files over 400 lines, of which 9 carry a hand-written
  Reading Guide and 18 carry none - `reference-sprint.md` at 827 lines among them
- **When** `docgen.py reading-guides` runs
- **Then** all 27 carry one, inside generation markers, and the 9 hand-written ones are replaced
  by generated equivalents so there is one shape rather than two
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docgen.py::ReadingGuideTests::test_every_reference_over_the_threshold_has_one

### AC2: each entry carries a LINE SPAN, not only an anchor

- **Given** a generated guide
- **When** an agent reads it
- **Then** each section entry carries its start and end line, so a partial read is
  `Read(offset, limit)` rather than a grep. That is strictly more than the 9 hand-written guides
  offer, and it is the difference between a table of contents and something that saves a read
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docgen.py::ReadingGuideTests::test_each_entry_carries_a_line_span

### AC3: the spans are TRUE of the file, and stay true when it changes

- **Given** a reference whose sections have moved since its guide was generated
- **When** `docgen.py reading-guides --check` runs
- **Then** it reports the drift. A line span that is wrong is worse than none: it sends a reader
  to the wrong place with confidence, where an anchor at least fails visibly
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docgen.py::ReadingGuideTests::test_a_moved_section_is_reported_as_drift

### AC4: no file is split and no budget is raised to fit the guide

- **Given** the guides add roughly 15 lines to each of 27 files, several already inside the
  budget tolerance
- **When** the budgets are checked afterwards
- **Then** they pass, because US0657 recorded the ceilings first. Splitting a reference to fit a
  guide would be the tail wagging the dog, and raising a ceiling to accommodate a generator is
  the ratchet running backwards
- **Verify:** pytest tools/tests/test_check_budgets.py::DriftTests::test_the_budgets_pass_with_the_guides_in_place

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | generate a guide only where one is absent, leaving the 9 hand-written ones as a second shape | every reference over the threshold carries one |
| AC2 | emit the anchor without the line span | each entry carries a LINE SPAN |
| AC3 | report no drift when a section has moved | the spans are TRUE of the file |
| AC4 | raise a ceiling to fit the generated guide | no file is split and no budget is raised |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
