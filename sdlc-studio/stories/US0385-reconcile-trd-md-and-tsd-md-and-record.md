# US0385: reconcile trd.md and tsd.md and record the findings

> **Status:** Draft
> **Delivers:** CR0385
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0141
> **Points:** 2
> **Affects:** sdlc-studio/trd.md, sdlc-studio/tsd.md, sdlc-studio/stories/US0385-reconcile-trd-md-and-tsd-md-and-record.md

## User Story

**As a** reader of this project's own spec, and of the spec-truth checks that read it
**I want** the mutation entries in trd.md and tsd.md to match what ships, and the pass to record every claim it checked
**So that** a criterion that deletes tests is not built on a superseded evidence shape, and the next reader can tell a claim that was verified from one that was never looked at

## Known divergences to reconcile

Four entries describe the single-blob model only:

- `trd.md` artefact table: `mutation-report.json` is listed with no sibling row for
  `mutation-runs.json`, so the ledger is absent from the artefact inventory.
- `tsd.md` mutation table, Output row: names the report, the git rev and a content hash per
  target, with no ledger.
- `tsd.md` mutation table, Gate row: "a rev change or an edited target reads STALE" - the
  superseded whole-blob rule.
- `tsd.md` gate-lane table: the `mutation` lane is described as reporting nothing beyond the
  report, not as judging per-file coverage.

## Acceptance Criteria

### AC1: both documents match the shipped ledger and coverage model

- **Given** the four divergences above
- **When** a reader compares each entry with `mutation.py` and the gate's coverage lane
- **Then** every entry names the ledger as the gate's source, states the per-file content-hash
  key, and states the covered / stale / uncovered verdict in place of the whole-blob rule;
  the report keeps its own row, since it is still written and still carries the survivors
- **Verify:** manual diff each of the four entries against mutation.py and gate.py, confirming no statement remains that only the report exists

### AC2: the pass records what was checked, not only what was changed

- **Given** the mutation-related claims in both documents, including those found correct
- **When** the reconcile pass finishes
- **Then** a findings table in this story lists every claim checked with its file, its verdict
  (correct, incomplete or false) and what was done, so a claim nobody examined is
  distinguishable from one examined and left alone
- **Verify:** manual confirm the findings table exists, covers every mutation claim in both files, and carries a verdict per row including the unchanged ones

## Notes

Both files feed the spec-truth checks. Their revision-history tables take a row for this pass,
naming the reconcile rather than describing it as an edit.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed: real ACs + Affects authored |
