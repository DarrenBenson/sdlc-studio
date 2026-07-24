# US0353: refine apply and add accept a --breakdown file, validated whole before minting, equivalent to the --story form

> **Status:** Draft
> **Delivers:** CR0343
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0120
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py

## User Story

**As a** delivery agent refining a triaged backlog
**I want** to hand `refine` the whole breakdown as a file
**So that** a bulk decomposition can be reviewed and version-controlled as data before it
mints anything, instead of being assembled as long fragile shell lines whose faults surface
one at a time at mint time.

## Acceptance Criteria

### AC1: a breakdown file mints exactly what the repeated --story form mints

- **Given** a breakdown file naming the epic title and the stories (title, points, affects)
- **When** `refine apply --breakdown FILE` runs against the same request as the equivalent
  `--story` command line
- **Then** the two produce the same units - same titles, points and Affects - so the file is
  an input form, not a second decomposition path
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::BreakdownFileTests::test_a_breakdown_file_mints_the_same_units_as_repeated_story_flags
- **Verified:** yes (2026-07-24)

### AC2: the whole file is validated before anything is minted

- **Given** a breakdown whose stories carry several faults (off-scale points, a missing
  title, a misspelled key)
- **When** it is applied
- **Then** the refusal names every fault at once, and nothing is written - no epic, no
  story, the request still undecomposed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::BreakdownFileTests::test_an_invalid_breakdown_mints_nothing_and_names_every_fault
- **Verified:** yes (2026-07-24)

### AC3: the file may name the epic title or the --into target

- **Given** a breakdown carrying `into: EPxxxx` instead of an epic title
- **When** it is applied
- **Then** the stories are minted under that existing epic, as `--into` does
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::BreakdownFileTests::test_the_file_may_name_the_into_target
- **Verified:** yes (2026-07-24)

### AC4: JSON and YAML are the same breakdown

- **Given** the same breakdown written as JSON and as YAML
- **When** each is applied
- **Then** both mint the same units; a YAML file with no parser installed is refused by
  name, not by a parse error about the file
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::BreakdownFileTests::test_yaml_and_json_forms_are_equivalent
- **Verified:** yes (2026-07-24)

### AC5: refine add takes a breakdown too

- **Given** an already-decomposed request and a breakdown naming the further epic
- **When** `refine add --breakdown FILE` runs
- **Then** the further epic and its stories are minted, with the epic title taken from the
  file when the flag is absent
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::BreakdownFileTests::test_add_takes_a_breakdown_and_its_epic_title
- **Verified:** yes (2026-07-24)

### AC6: the two input forms are alternatives, never layers

- **Given** `--breakdown` passed alongside `--story`
- **When** the command runs
- **Then** it is refused with nothing minted - a file under review that disagrees with the
  command that actually ran is worse than either form alone
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::BreakdownFileTests::test_breakdown_and_story_flags_together_are_refused
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed: six ACs authored against the slice, each with an executable Verify |
| 2026-07-24 | sdlc-studio | Built: `--breakdown FILE` on `apply` and `add` (JSON or YAML), one whole-file validation collecting every fault before any mint, `BreakdownFileTests` in `test_refine.py` |
