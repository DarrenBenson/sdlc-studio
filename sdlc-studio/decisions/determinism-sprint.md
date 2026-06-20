# Decisions Ledger - determinism-sprint

> Append-only. One row per ruling; earlier rulings are never rewritten.

| At | Decision | Rationale |
| --- | --- | --- |
| 2026-06-20T13:05:26Z | Sprint = CR0016 (sharpen AC) + close CR0018, then CR0003/CR0004/CR0008 (+CR0007 stretch) | operator-approved triage; CR0016 first so audit CRs are verifiable (tautology AC pass vacuously, BG0003 class) |
| 2026-06-20T13:10:46Z | Add tranche-audit step to autosprint (CR0021); CR0003 integrity is its link-integrity lens | operator: tranche readiness should be a defined loop step, not improvised - sprint-zero proved the need |
| 2026-06-20T13:28:13Z | audit.py _weak_ac gated to the AC section only | critic REJECT: AC markup outside the section let prose-only CRs pass as ready |
| 2026-06-20T13:38:15Z | review_prep uses git %cI committer time (CR0004) | reproducible across clones; st_mtime fallback only when untracked; datetime compare; malformed->needs+warn |
