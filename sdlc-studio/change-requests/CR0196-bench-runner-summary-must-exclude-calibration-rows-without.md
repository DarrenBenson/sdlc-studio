# CR-0196: Bench runner: summary must exclude calibration rows without hand-filtering

> **Status:** Complete
> **Created:** 2026-07-08
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** tooling

## Summary

Repo-only (`tools/bench/`, not in the skill payload). Protocol v2 forbids pooling
calibration rows with measured rows, but `runner.py summary` aggregates everything in
`runs.jsonl`. Producing the N=5 report required hand-filtering rows into a temp file and
monkey-patching `RESULTS_PATH` - exactly the kind of manual step that will one day be
forgotten, silently pooling calibration data into a published aggregate. The tool should
enforce what the protocol declares.

Change: `record` gains a `--phase {calibration,measured}` field (default measured;
existing rows backfilled once); `summary` excludes non-measured rows by default and gains
`--include-phase` to opt calibration rows back in explicitly. Alternative considered: a
`--exclude-run-id` filter - rejected as it encodes the protocol rule in the operator's
memory instead of the data.

## Acceptance Criteria

- [ ] `record` writes a `phase` field; existing rows in `runs.jsonl` are backfilled
      (v2n1 rows = calibration, spike/measured rows = measured)
- [ ] `summary` excludes calibration rows unless explicitly included via a flag
- [ ] Unit test: a calibration row present in the file does not move any measured
      aggregate
- [ ] `docs/benchmarks/protocol-v2.md` unchanged (frozen); the behaviour is documented in
      the bench README/help text

## Evidence

- N=5 report production (D0014): first summary run pooled v2n1 calibration rows into the
  Tier-1 means (n=6 cells instead of n=5) and was caught by eye, not by the tool.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-08 | sdlc | Created via `new` (deterministic) |
| 2026-07-08 | claude | Filed from N=5 benchmark finding (D0014) |
