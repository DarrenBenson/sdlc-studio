# US1230: The TRD template gains a Reliability and Observability section for dependency failure and required signals

> **Status:** Draft
> **Risk-class:** elevated
> **Delivers:** CR0691
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/core/trd.md, .claude/skills/sdlc-studio/reference-trd.md, .claude/skills/sdlc-studio/scripts/tests/test_trd_reliability_section.py
> **Epic:** EP0338
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The TRD template gains a Reliability and Observability section for dependency failure and required signals
**So that** CR0691 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The TRD template declares dependency failure behaviour and required signals

- **Given** the shipped TRD template
- **When** its sections are read
- **Then** it has a Reliability and Observability section holding a table with one row per external dependency (the behaviour when it fails, one of fail the request, return a partial result or return a default, with its timeout and its retry policy) and a list of the observability patterns every change must keep (a structured log line with a correlation id on the failure path, error and latency metrics, a health check, an alert on a declared failure), every value a template placeholder in the template's own form. Fails on: a section with prose only and no per-dependency row, or a literal value where a placeholder belongs
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_trd_reliability_section.py::TrdReliabilitySectionTests::test_the_template_has_a_row_per_dependency_and_the_required_signals

### AC2: The TRD reference says how to fill the section

- **Given** `reference-trd.md`
- **When** its guidance for the template's sections is read
- **Then** it names the Reliability and Observability section by the template's own heading, says what each column takes and that the engineering review reads the section, and its contents table lists the new part at the right lines. Fails on: a reference that names a heading the template does not carry, or a contents table left stale
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_trd_reliability_section.py::TrdReliabilitySectionTests::test_the_reference_names_the_section_and_how_to_fill_it

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
