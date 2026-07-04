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
| D0001 | Sprint 2026-07: CR0139 merged into CR0132 (both ACs carried over); mixed batch = CR0132,CR0133,CR0134,CR0135,CR0136,CR0138 + BG0045,BG0046 | Two field reports of the same self-diagnosing-findings defect; operator approved the merge and the 9-unit mixed batch at the plan STOP. Mixed-batch planning friction re-confirmed first-hand (sprint.py plan flags mutually exclusive, sprint-plan.json single path) - evidence for CR0138. | accepted | -- | 2026-07-04 |
| D0002 | RFC0022 Accepted as recommended: declared textual mutations as the portable core, mutation-framework adapters as an opt-in lane, static assertion scan as pre-filter; D1-D6 settled at epic design within that direction. CR0134 unblocked and built in sprint 2026-07-B (operator: build it all now). | Operator decision at sprint-2 triage (2026-07-04). Also decided: sweep the 44 historical Fixed bugs to Closed as a recorded convention sweep (none production-affecting; not fresh verification), and progress RFC0018 to a concrete recommendation. | accepted | -- | 2026-07-04 |

## Notes

- Decisions are numbered globally and zero-padded: `D{NNNN}`.
- Append with `scripts/decisions.py add`; list with `scripts/decisions.py list`.
- `Status`: `accepted` | `superseded` | `revisited`. A superseding decision names the one
  it replaces in `Supersedes`.
- Distinct from the sprint per-tranche ledger (`scripts/ledger.py`), which is scoped to
  a single delivery run; this is the durable project spine.
