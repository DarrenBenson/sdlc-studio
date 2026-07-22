# US0292: Report an Affects line the unit's own content contradicts, at plan time

> **Status:** Done
> **Delivers:** CR0347
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/validate.py
> **Epic:** EP0095
> **Points:** 3

## User Story

**As an** operator reading a plan before fanning a batch out
**I want** each unit whose `Affects` its own content contradicts named in the plan
**So that** a wrong declaration is corrected before the waves are built on it, not after two
agents collide

## Context

CR0347 records four artefacts in one run naming the wrong files: one named only a file it would
create, one named 2 of the 5 files its parent required, one named `reconcile.py` when its real
surface was three other scanners, and one whose tranche was three short. Correcting the third
dissolved a recorded collision and left the real one standing.

`breakdown` sees most of this already and says nothing. It computes `unresolvable` for every
declared path, then reports it only when EVERY path fails - the "fictional Affects" case. A unit
declaring four real files and one typo is reported as fully groomed, and the typo surfaces
whenever a human next reads the artefact.

The other half is the inverse: a unit whose ACs name a file its `Affects` omits. US0291 derives
those paths for the cluster analysis; this story reports the mismatch between them and the
declaration.

Advisory, not blocking. A path to a file the unit will CREATE cannot resolve yet, so an
unresolved path is legitimate as often as it is a typo, and the grooming gate's verdict is
unchanged by this report. `validate` gains the same check off the same predicate so one artefact
can be checked without building a plan.

## Acceptance Criteria

### AC1: a partly unresolvable Affects is reported at plan time

- **Given** a unit declaring several files of which one does not resolve on disk
- **When** the batch breakdown runs
- **Then** that path is named in the plan against that unit, where today it is reported only when
  no declared path resolves at all
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_a_partly_unresolvable_affects_is_reported
- **Verified:** yes (2026-07-22)

### AC2: a file the unit's ACs name but its Affects omits is reported

- **Given** a unit whose Verify lines target a file absent from its `Affects`
- **When** the breakdown runs
- **Then** that file is named against the unit as an omission from the declaration
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_a_file_the_acs_name_but_affects_omits_is_reported
- **Verified:** yes (2026-07-22)

### AC3: the report changes nothing the gate decides

- **Given** a unit carrying both defects that is otherwise groomed and within the split ceiling
- **When** the breakdown runs
- **Then** it stays in `groomed`, the breakdown's `ok` verdict is unchanged, and the plan is not
  refused, because a path to a file the unit will create is legitimate
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_the_affects_advisory_never_changes_the_grooming_verdict
- **Verified:** yes (2026-07-22)

### AC4: validate reports the same mismatch on a single artefact

- **Given** one story file with a contradicted `Affects`
- **When** `validate` checks it
- **Then** it reports the same paths as a warning, from the same predicate the planner uses, so
  the two cannot drift into disagreeing about what a contradicted `Affects` is
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py -k test_validate_reports_an_affects_the_story_contradicts
- **Verified:** yes (2026-07-22)

## Open Questions

- [ ] CR0347 does not say how to tell a path to a file the unit will legitimately create from a
  typo or a stale rename. Both read as unresolvable on disk, so AC1 reports the path and leaves
  the judgement to the reader rather than guessing - Owner: operator

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Groomed against CR0347 AC2 and breakdown's existing unresolvable computation |
