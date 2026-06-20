# BG-0021: escaped-pipe split bug present in three more table parsers

> **Status:** Fixed
> **Severity:** Medium
> **Reporter:** agent-crew (relayed) + systemic audit
> **Date:** 2026-06-20
> **Affects:** scripts/critic.py, scripts/rfc.py, scripts/ledger.py, scripts/lib/sdlc_md.py
> **Related:** BG0020, CR0026 (the reconcile index parser was fixed there)
> **GitHub Issue:** --

## Summary

The reconcile index parser was fixed to honour escaped pipes (`\|` in a cell) under
CR0026, and that fix is live (agent-crew epics drift went to 0). A follow-up agent-crew
report re-flagged the class. Auditing every table parser in the skill found the same
raw `split("|")` in three more readers:

- `critic.py` `read_verdicts` - reads `critic-verdicts.md`.
- `rfc.py` `_table_data_rows` - reads Open-Decisions / Workstreams tables in RFCs.
- `ledger.py` `read_ledger` - reads the per-tranche decisions ledger.

## Exposure

- **rfc.py: real.** RFC tables are human-authored, so a cell may legitimately contain
  `\|` (the report's `EP0230 All\|Crew` case). A naive split adds a phantom column and
  misreads later cells.
- **critic.py / ledger.py: defensive.** Both write rows through `_clean`, which replaces
  a literal `|` with `/`, so their own rows never contain `\|`. The raw split was still
  wrong-in-principle and is unified for safety.

## Fix

Promote the escaped-pipe-aware splitter to the shared library as
`sdlc_md.table_cells(line)` (split on UNescaped pipes, unescape `\|`, return None for a
separator / non-table line) and route all four parsers (reconcile, critic, rfc, ledger)
through it - one splitter, no per-script drift.

## Acceptance Criteria

- [x] `sdlc_md.table_cells` honours `\|`, returns None for separators / non-table lines, and is unit-tested.
- [x] reconcile, critic, rfc, ledger all delegate to it (no remaining raw `split("|")` in a table parser).
- [x] An RFC workstream/decision cell containing `\|` parses without column shift (unit-tested).
- [x] Full suite green; reconcile drift 0 across our scopes.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (BG0021) | Fixed - shared `sdlc_md.table_cells`; reconcile/critic/rfc/ledger unified; rfc was the real exposure (human-authored tables) |
| 2026-06-20 | agent-crew (relayed) | Re-flagged the escaped-pipe class after the index-parser fix; audit found 3 more parsers |
