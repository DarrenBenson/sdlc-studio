# US1222: Story and bug templates take a Capture line, and a lint flags a reader of another tool's output without one

> **Status:** Draft
> **Risk-class:** elevated
> **Delivers:** CR0682
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/core/story.md, .claude/skills/sdlc-studio/templates/core/bug.md, .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Epic:** EP0333
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Story and bug templates take a Capture line, and a lint flags a reader of another tool's output without one
**So that** CR0682 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The templates carry an optional Capture line and refine asks for it

- **Given** the story and bug templates, and a request refined into a unit whose Affects names a `meter_*.py` or `*_hook.py` reader
- **When** the templates are read and `refine.py` mints the unit
- **Then** both templates carry an optional `Capture:` line for the producer, its version and the recorded sample's path, and the minted unit carries the line to fill with refine's output asking for it; a unit that reads no other tool's output is minted without it. Fails on: a template with no Capture line, or refine minting a reader unit without asking
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::CaptureLineTests::test_refine_asks_for_a_capture_on_a_unit_that_reads_another_tools_output

### AC2: The lint flags a reader unit with no Capture line

- **Given** an open unit whose Affects names `meter_sample.py`, one whose Affects names `sample_hook.py`, the same two with a filled Capture line, and a unit naming neither
- **When** `validate.py` checks each file
- **Then** the first two are flagged naming the unit and the reader file, and the other three are not. Fails on: a reader unit passing with no capture, or a unit that reads no tool's output flagged
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::CaptureLintTests::test_a_reader_unit_without_a_capture_is_flagged

### AC3: An unfilled or partial Capture line does not satisfy the lint

- **Given** a reader unit whose Capture line is still the template's unfilled text, one that names a producer and no sample path, and one whose sample path names a file that does not exist
- **When** `validate.py` checks each file
- **Then** each is flagged naming the part that is missing. Fails on: an empty Capture line read as a recorded sample
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::CaptureLintTests::test_an_unfilled_or_partial_capture_is_flagged

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
