# US0653: The verb catalogue is generated from the parsers, never typed

> **Status:** Ready
> **Delivers:** CR0538
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/docgen.py, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/scripts/tests/test_docgen.py
> **Epic:** EP0211
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The verb catalogue is generated from the parsers, never typed
**So that** CR0538 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: the catalogue is GENERATED, and typing into it is refused

- **Given** `reference-scripts-surface.md`, whose verb table sits between
  `<!-- BEGIN GENERATED -->` and `<!-- END GENERATED -->` markers
- **When** `docgen.py surface` runs
- **Then** it rewrites only what lies between those markers and leaves every byte outside them
  alone, and a target file carrying no markers is REFUSED rather than overwritten. The marker
  discipline is what makes this generation rather than a rewrite: a generator that owns a whole
  file eventually eats a paragraph somebody wrote
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docgen.py::GeneratedRegionTests::test_only_the_marked_region_is_rewritten_and_an_unmarked_file_is_refused

### AC2: `--check` reports drift and exits 0

- **Given** a catalogue with one verb's description edited by hand, and a second fixture with
  none
- **When** `docgen.py surface --check` runs on each
- **Then** the first prints a non-zero drift count and the second prints zero, and BOTH exit 0.
  Exit 0 is the criterion, not an oversight: the operator's decision is that these guards report
  and never block, so a lane that fails a commit on documentation drift is the thing being
  refused here
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docgen.py::GeneratedRegionTests::test_check_reports_drift_and_exits_zero

### AC3: the catalogue lists every verb the surface enumerates, and no other

- **Given** the surface library's enumeration
- **When** the catalogue is generated
- **Then** every enumerated verb appears exactly once and nothing appears that the enumeration
  did not produce - so the page cannot drift into describing a verb that was removed, which is
  the failure the audit found in the other direction
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docgen.py::GeneratedRegionTests::test_the_catalogue_lists_exactly_what_the_surface_enumerates

### AC4: flags are not in the markdown, and the page says where they are

- **Given** 677 flags across the surface
- **When** the catalogue is read
- **Then** it carries none of them, and states that `--help` and `docgen surface --format json`
  answer WHAT FLAGS while the page answers WHETHER A VERB EXISTS. 677 rows would need a budget
  allowlist entry on the day the page was born, and a page nobody can afford to keep is one that
  goes stale rather than one that helps
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docgen.py::GeneratedRegionTests::test_the_page_carries_no_flags_and_names_what_does

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | write the whole target file rather than only the marked region | the catalogue is GENERATED |
| AC1 | generate into an unmarked file rather than refusing it | the catalogue is GENERATED |
| AC2 | exit non-zero when `--check` finds drift | `--check` reports drift and exits 0 |
| AC3 | emit only the verbs whose script name sorts first, truncating the list | the catalogue lists every verb |
| AC4 | render each verb's flags into the table beside it | flags are not in the markdown |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
