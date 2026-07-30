# BG0438: audit-run provenance is not durable: the register and the row accessor disagree, so a seeded run can pass as measured

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/audit_cost.py, .claude/skills/sdlc-studio/scripts/tests/test_audit_cost.py
> **Evidence:** Executed by an independent reviewer, who confirmed no live verdict is currently wrong.
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch); agent; skill v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

`register` folds rows with LAST-row-wins while `run_row` returns the FIRST match, `record` appends unconditionally, and nothing guards a duplicate `run_id.` So appending a plain `record` after a seeded row flips the register's provenance from backfilled to recorded while the row accessor still says backfilled - the two readers of one ledger disagree about the same id, and a seeded id silently passes as measured through the one `detector_owed` reads. The reverse (downgrading a measured run) is equally unguarded and no test covers a duplicate `run_id.` Separately, `record()` accepts any provenance string: PROVENANCES is enforced only at the argparse layer, so a library caller can write a third provenance neither reader understands. Also `registered_run_ids` discards the three-state read, returning `{}` for a corrupt register whose docstring says 'empty when none is recorded'.

## Steps to Reproduce

1. Seed a run as backfilled, then `record` the same `run_id` with the default provenance.
2. `register` reports 'recorded'; `run_row` reports 'backfilled'.
3. `record(root, {'run_id': 'wf_x', 'provenance': 'measured-by-vibes'})` is written and read back verbatim.

## Proposed Fix

Make the fold order explicit and identical in both readers, refuse or merge a duplicate `run_id`, validate the provenance in `record` rather than only in argparse, and give `registered_run_ids` the same three-state return as `register`.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `register` folds rows with LAST-row-wins while `run_row` returns the FIRST match, `record` appends unconditionally, and nothing guards a duplicate `run_id.` So...
- [ ] The proposed fix lands, pinned by a test: Make the fold order explicit and identical in both readers, refuse or merge a duplicate `run_id`, validate the provenance in `record` rather than only in...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch) | Filed |
