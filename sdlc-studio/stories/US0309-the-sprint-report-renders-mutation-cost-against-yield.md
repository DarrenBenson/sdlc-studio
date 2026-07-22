# US0309: The sprint report renders mutation cost against yield for the run and the trailing history

> **Status:** Review
> **Delivers:** CR0379
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py,.claude/skills/sdlc-studio/scripts/mutation.py
> **Epic:** EP0104
> **Points:** 3

## User Story

**As an** operator deciding at the close whether the mutation gate is worth its wall-clock
**I want** the sprint report to show what the gate cost against what it found, for this run and
for the runs before it
**So that** the decision to keep or cut it rests on the recorded series rather than on whether
this particular run happened to feel slow

## Context

CR0379 AC4. The other stories in this request make the evidence exist: US0301 writes a per-run
row carrying applied, killed, survived, un-checked and elapsed seconds, and US0302 links the
artefacts filed from survivors back to the run that found them. Neither puts the two halves in
front of the person who takes the decision. The close is where the decision is actually taken,
so that is where the trade belongs.

Asked directly at the RUN-01KY03GS close, the best available answer had to be reconstructed by
hand from timeouts and timestamps. A gate that cannot show its yield gets cut on a bad day and
kept on a good one.

## Acceptance Criteria

### AC1: The report renders this run's mutation cost beside its yield

- **Given** a run whose mutation series holds a row with counts and an elapsed time, and
  artefacts filed against that run id
- **When** the sprint report is rendered
- **Then** it shows the run's wall-clock cost, its mutant counts, and the artefacts attributed
  to it, in one place rather than in three separate sections
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py -k test_the_report_renders_mutation_cost_beside_yield
- **Verified:** yes (2026-07-22)

### AC2: The trailing history is shown, not only the current run

- **Given** a series holding rows for several previous runs
- **When** the sprint report is rendered
- **Then** the trailing rows are shown alongside the current one, so a single cheap or
  expensive run cannot be mistaken for the trend
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py -k test_the_report_shows_the_trailing_mutation_history
- **Verified:** yes (2026-07-22)

### AC3: A run with no mutation evidence is named as such, never rendered as a zero-yield run

- **Given** a run whose mutation step was skipped, refused or killed, so no series row exists
- **When** the sprint report is rendered
- **Then** it states that the run recorded no mutation evidence, and does not render counts of
  zero, which would read as a run that found nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py -k test_a_run_without_mutation_evidence_is_named_not_zeroed
- **Verified:** yes (2026-07-22)

### AC5: A series row is only this sprint's when it was written inside this run

- **Given** a project-wide mutation series holding a PREVIOUS sprint's row, and a run being
  reported that wrote none of its own
- **When** the sprint report is rendered
- **Then** the previous row is shown as a previous run and never as this run's figures, and this
  run is named as having no mutation evidence; a run state whose batch does not name this
  sprint's units attributes nothing and says why
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py -k MutationBelongsToThisRunTests
- **Verified:** yes (2026-07-22)

### AC4: Cost per finding is derived only where both halves are present

- **Given** a run with an elapsed time but no attributed artefacts, and a second run with both
- **When** the report derives a cost-per-finding figure
- **Then** it derives one only for the second run, and states why the first has none, rather
  than dividing by zero or printing a blank that reads as free
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py -k test_cost_per_finding_is_derived_only_where_both_halves_exist
- **Verified:** yes (2026-07-22)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | claude | Repair round 1 - `current` was the newest row of the PROJECT-WIDE series whatever run wrote it, so a sprint that ran no mutation republished the previous sprint's cost and yield as its own, unlabelled, while the rows below were correctly prefixed `previous run`. AC1 and AC3 were both false on that path. The row is now joined to the run's own measured window, by the same guard `_sprint_goal` uses; AC5 added |
