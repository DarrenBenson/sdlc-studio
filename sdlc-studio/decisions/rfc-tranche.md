# Decisions Ledger - rfc-tranche

> Append-only. One row per ruling; earlier rulings are never rewritten.

| At | Decision | Rationale |
| --- | --- | --- |
| 2026-06-20T20:35:37Z | Deliver all 4 outstanding Accepted RFCs together: RFC0004, RFC0008, RFC0007, RFC0002 (7 CRs); deps-first RFC0004->0008->0007->0002(WS3->WS1->WS2) | user: deliver all outstanding rfcs together; WS4/WS5 of RFC0002 stay deferred per its Decision |
| 2026-06-20T21:04:17Z | Tranche complete: all 4 outstanding Accepted RFCs delivered (RFC0004/CR0032, RFC0008/CR0033, RFC0007/CR0034, RFC0002/CR0035-37) | 7 CRs, 363 tests green, drift 0, conformance clean, installed==repo; only RFC0005/RFC0012 remain (Draft, deferred) + RFC0002 WS4/WS5 deferred |
