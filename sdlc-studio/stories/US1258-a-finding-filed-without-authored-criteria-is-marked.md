# US1258: A finding filed without authored criteria is marked ungroomed in its file and at filing, naming the flags that supply criteria

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0708
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Epic:** EP0348
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** A finding filed without authored criteria is marked ungroomed in its file and at filing, naming the flags that supply criteria
**So that** CR0708 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A finding filed without criteria carries the ungroomed mark and is told so

- **Given** a bug filed through `file_finding.py file` with no `--ac`, whose evidence is long enough for criteria to be derived
- **When** the file is written
- **Then** its `## Acceptance Criteria` section opens with the ungroomed mark `sdlc_md.UNGROOMED_AC_TOKEN` above the derived checkboxes, and the filing output says the finding is ungroomed and names `--ac` and `--verify` as the flags that supply authored criteria. Fails on: derived stubs written with no mark, so the bug reads as groomed until a grooming pass opens it, or a notice that names no flag
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::UngroomedMarkTests::test_a_finding_without_ac_is_marked_ungroomed_and_names_the_flags

### AC2: A finding filed with authored criteria carries no mark

- **Given** the same bug filed with `--ac` and a paired `--verify`
- **When** the file is written
- **Then** the section holds the authored criterion with its Verify line and no ungroomed mark, and the filing output carries no ungroomed notice. Fails on: the mark stamped on authored criteria, which would have `sprint plan` refuse a groomed bug
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::UngroomedMarkTests::test_a_finding_with_authored_criteria_carries_no_mark

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
