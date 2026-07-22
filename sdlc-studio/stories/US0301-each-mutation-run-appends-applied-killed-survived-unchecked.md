# US0301: Each mutation run appends applied, killed, survived, unchecked and wall-clock to a series

> **Status:** Draft
> **Delivers:** CR0379
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py
> **Epic:** EP0100
> **Points:** 3

## User Story

**As a** sprint operator deciding at a close whether the mutation gate is worth its wall-clock
**I want** every mutation run to append one durable row recording what it applied, killed, survived, left un-checked beyond the ceiling, and how long it took
**So that** the gate is judged on its own accumulated record rather than on whichever run happened last

## Context

Today `mutation.py run` writes two files: `sdlc-studio/.local/mutation-report.json`, which is
last-write-wins for the latest run, and `sdlc-studio/.local/mutation-runs.json`, the per-target
evidence ledger keyed on target and content hash. Neither is a per-run series: the report is
overwritten by the next run and the ledger deliberately supersedes a target's earlier numbers.
Nothing records elapsed time at all - `mutation.py` has no timing call. So the question CR0379
asks cannot be answered from disk, and at the RUN-01KY03GS close it had to be reconstructed by
hand from timeouts and file timestamps.

This story adds the missing third file: an append-only per-run series, in the shape
`verify_ac.py` already uses for `verify-history.jsonl` (one JSON object per line). The summary
counts it needs are already computed (`summary.applied/killed/survived/errors/unviable/truncated`,
`len(report["unchecked"])`); only the wall-clock and the append are new. This story records the
series. Counting yield against it is US0302.

## Acceptance Criteria

### AC1: A completed run appends one row carrying its counts and its wall-clock

- **Given** a repository with a target file and a test command that kills at least one mutant
- **When** `mutation.py run` completes and writes its report
- **Then** exactly one line is appended to the series file, carrying the run's `applied`,
  `killed`, `survived`, `unchecked` and `elapsed_s` values plus the git revision and timestamp
  that identify the run, and `elapsed_s` is a measured positive duration rather than a constant
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_mutation.py -k MutationSeriesRowTests
- **Verified:** yes (2026-07-22)

### AC2: A refused, errored or timed-out run is recorded as producing no evidence

- **Given** a run that is refused by the baseline guard, or that ends without any killed or
  survived verdict
- **When** the series row for that run is read back
- **Then** the row carries an explicit no-evidence outcome and zero yield, so a reader summing the
  series cannot count it as a clean run, and a run reporting zero survivors after applying nothing
  is distinguishable from a run reporting zero survivors after applying twenty mutants
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_mutation.py -k MutationSeriesNoEvidenceTests
- **Verified:** yes (2026-07-22)

### AC3: The series accumulates and never silently loses or corrupts earlier runs

- **Given** a series file already holding rows from earlier runs
- **When** a further run appends to it, and separately when the file is unreadable or malformed
- **Then** the earlier rows are still present and byte-identical after the append; a malformed
  file is replaced rather than crashing the run and the replacement is reported on stdout; and a
  `--dry-run` run appends nothing
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_mutation.py -k MutationSeriesAppendTests
- **Verified:** yes (2026-07-22)

## Open Questions

- CR0379 lists `sprint_report.py` in its Affects and asks for cost rendered against yield at the
  close, but no story in EP0100 carries that rendering. Either a third story is needed or the
  epic closes short of its fourth acceptance criterion.
- The CR does not state a retention bound for the series. `mutation.py` bounds its ledger at
  `LEDGER_LIMIT` entries with a cumulative dropped count; whether the run series takes the same
  treatment, or is unbounded because a row is small and the trailing history is the point, is
  unspecified.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Groomed: user story and acceptance criteria authored |
