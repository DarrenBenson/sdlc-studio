# US0669: validate sweeps the existing corpus for unresolvable selectors, giving unresolvable_stamps its first caller

> **Status:** Done
> **Delivers:** CR0508
> **Created:** 2026-08-11
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Epic:** EP0215
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** validate sweeps the existing corpus for unresolvable selectors, giving unresolvable_stamps its first caller
**So that** CR0508 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1

- **Given** an artefact already in the corpus whose `Verify:` line resolves to nothing
- **When** `validate.py check` is run
- **Then** it is REPORTED by id and selector, so the existing corpus is swept rather than only new
  writes being guarded. `unresolvable_stamps` already does this work and has had no caller.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py -k validate_reports_an_unresolvable_verify_selector
- **Verified:** yes (2026-08-11)
- **Mutant:** in `validate.py`, drop the unresolvable-selector sweep from the check.

### AC2

- **Given** an artefact whose selectors all resolve, and one whose selector cannot be judged
- **When** the same check runs
- **Then** neither is reported, so the sweep discriminates rather than flagging the corpus.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py -k the_sweep_reports_only_what_it_can_judge_and_finds_absent
- **Verified:** yes (2026-08-11)
- **Mutant:** in `validate.py`, report every selector the sweep examines.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `validate.py`, remove the unresolvable-selector sweep from the check | |
| AC2 | in `validate.py`, change the sweep to report every selector it examines | |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-11 | sdlc-studio | Created via `new` (deterministic) |
