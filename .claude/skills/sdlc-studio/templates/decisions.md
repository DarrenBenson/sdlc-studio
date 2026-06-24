<!--
Template: Project Decisions Log
File: sdlc-studio/decisions.md
Maintained by: scripts/decisions.py (add / list)
Related: reference-scripts.md, help/init.md
-->
# Project Decisions Log

The canonical, append-only home for load-bearing decisions every later artifact and
delegated agent inherits - both **product** decisions (scope cuts, the answers to the
PRD's open questions) and **implementation conventions** (error-envelope shape, ID scheme,
token strategy, migration style, test harness). One record, two views: an open question
lives in `PRD §Open Questions`; when resolved it is promoted here with a back-link, never
duplicated as free text in both. This block is injected into the handoff context delegated
agents read, so a decision is referenced once, not pasted N times.

## Decisions

| ID | Decision | Rationale | Status | Supersedes | Date |
| --- | --- | --- | --- | --- | --- |

## Notes

- Decisions are numbered globally and zero-padded: `D{NNNN}`.
- Append with `scripts/decisions.py add`; list with `scripts/decisions.py list`.
- `Status`: `accepted` | `superseded` | `revisited`. A superseding decision names the one
  it replaces in `Supersedes`.
- Distinct from the autosprint per-tranche ledger (`scripts/ledger.py`), which is scoped to
  a single delivery run; this is the durable project spine.
