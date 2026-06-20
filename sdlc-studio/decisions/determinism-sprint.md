# Decisions Ledger - determinism-sprint

> Append-only. One row per ruling; earlier rulings are never rewritten.

| At | Decision | Rationale |
| --- | --- | --- |
| 2026-06-20T13:05:26Z | Sprint = CR0016 (sharpen AC) + close CR0018, then CR0003/CR0004/CR0008 (+CR0007 stretch) | operator-approved triage; CR0016 first so audit CRs are verifiable (tautology AC pass vacuously, BG0003 class) |
| 2026-06-20T13:10:46Z | Add tranche-audit step to autosprint (CR0021); CR0003 integrity is its link-integrity lens | operator: tranche readiness should be a defined loop step, not improvised - sprint-zero proved the need |
| 2026-06-20T13:28:13Z | audit.py _weak_ac gated to the AC section only | critic REJECT: AC markup outside the section let prose-only CRs pass as ready |
| 2026-06-20T13:38:15Z | review_prep uses git %cI committer time (CR0004) | reproducible across clones; st_mtime fallback only when untracked; datetime compare; malformed->needs+warn |
| 2026-06-20T13:41:05Z | config.py loader (PyYAML soft-dep); config-defaults.yaml authoritative; remove 12 doc yaml fences; drift-guard test (CR0008) | core scripts stay stdlib; only the new config helper needs yaml (skipUnless in tests); doc Default columns guarded against drift |
| 2026-06-20T13:49:17Z | status.py reads config via config.py (lazy/graceful) | critic REJECT: AC1 needed a real consumer, not just a loader; staleness_days moved to a guarded table row |
| 2026-06-20T13:54:53Z | resume skips ALL terminal statuses, matches primary Epic id (CR0007) | critic REJECT: Superseded/Won't-Implement/Deferred must not be resume points; multi-id Epic field must not over-match |
| 2026-06-20T14:05:44Z | Retro filed CR0022 (deps-order), CR0023 (conformance completion), widened BG0018, LL0007/LL0008 | run learnings: conformance is a partial oracle; critic unenforced; ordering ignores deps; status-parse fragility is a class |
