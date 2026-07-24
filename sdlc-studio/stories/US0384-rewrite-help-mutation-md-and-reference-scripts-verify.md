# US0384: rewrite help/mutation.md and reference-scripts-verify.md for the ledger, content-hash key, coverage verdict and advisory lane

> **Status:** Done
> **Delivers:** CR0385
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0141
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/help/mutation.md, .claude/skills/sdlc-studio/reference-scripts-verify.md

## User Story

**As an** agent or operator deciding when to run the mutation gate and how to read its verdict
**I want** the two documents I actually open to describe the ledger and the coverage verdict the gate now uses
**So that** I do not read a STALE warning under the superseded single-blob meaning, or judge a file's evidence from a report that is not the gate's source

## Current divergence

Both files describe `mutation-report.json` and the whole-blob freshness model only. Neither is
false - the report is still written unchanged - but neither mentions `mutation-runs.json`, the
bounded per-target ledger keyed on each file's content hash, which is now the only source the
gate lane reads for coverage. `help/mutation.md` says the lane "reports STALE on a rev change
OR any target edited since the run", which is the old rule.

## Acceptance Criteria

### AC1: help/mutation.md describes the ledger as the evidence surface

- **Given** a reader following help/mutation.md to understand what a run leaves behind
- **When** they read the outputs and the verdicts sections
- **Then** the file names `mutation-runs.json` alongside the report, states that an entry is
  keyed on the target's content hash so evidence survives commits to other files, states the
  200-entry bound and that truncation is counted as a dropped total rather than being silent,
  and distinguishes a measured entry from a registered self-report
- **Verify:** manual read help/mutation.md against mutation.py `append_ledger` and `LEDGER_LIMIT`, confirming each of those four statements is present and correct
- **Verified:** yes (2026-07-24, manual: help/mutation.md carries 8 ledger references against mutation.py:57-89 - LEDGER_LIMIT=200, oldest-first eviction, append_ledger's run-verdict mapping)

### AC2: reference-scripts-verify.md describes the coverage verdict and the fallback

- **Given** the catalogue entry for `mutation.py`, which today mentions only the report and the
  advisory lane
- **When** a reader looks up what the gate lane decides
- **Then** it states the per-file verdict vocabulary - hash matches means covered, hash differs
  or none recorded means stale, no entry means uncovered - and states that with nothing in the
  ledger to judge the lane degrades to the whole-report checks
- **Verify:** manual read reference-scripts-verify.md against gate.py `_mutation_coverage`, confirming the three verdicts and the degraded fallback are described
- **Verified:** yes (2026-07-24, manual: reference-scripts-verify.md describes covered/stale/uncovered and the fallback, against gate.py:312 `_mutation_coverage` and :452 `_mutation_coverage_safe`)

### AC3: the lane is stated as advisory, and staleness is readable without opening gate.py

- **Given** a reader who has only these two documents
- **When** they ask what makes a file's evidence stale and whether a finding blocks
- **Then** both answers are on the page: the file's content changed since the entry that
  covers it, and the lane never changes the exit code
- **Verify:** manual confirm both files state the lane is advisory and define staleness per file, with no reference to reading the source
- **Verified:** yes (2026-07-24, manual: both state the lane is advisory and key staleness on the per-file content hash)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed: real ACs + Affects authored |
| 2026-07-24 | sdlc-studio | Both files rewritten against `mutation.py` and `gate.py::_mutation_coverage`: the ledger, its content-hash key, the 200-entry bound and dropped total, measured against registered provenance, the covered / STALE / uncovered verdict, the degraded whole-report fallback, and the lane stated as advisory in both |
