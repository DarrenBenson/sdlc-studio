# CR-0210: consistent CLI argument grammar across the script family

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

Input-side sibling of the --format json parity item in the quality-debt CR: the scripts disagree on how lists and targets are passed, and each mismatch costs an agent a --help probe. Observed while driving the RV0007 sprint: audit.py check takes --ids comma-separated; sprint.py plan takes a worklist FILE; transition.py set takes --ids space-separated; artifact.py close requires --id while file_finding uses a positional subcommand with flag-only fields; ledger.py record wants --tranche/--decision where sibling recorders use --unit. One documented grammar (ids: repeatable --id or one comma list, everywhere; consistent recorder field names) plus aliases for the legacy spellings.

## Acceptance Criteria

- [ ] A documented argument convention (best-practices/script.md) covers id lists, target selection and recorder field names
- [ ] Every script accepting ids accepts the same form (with legacy aliases kept); a conformance test sweeps argparse definitions
- [ ] reference-scripts.md notes the grammar once instead of per-script exceptions

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
