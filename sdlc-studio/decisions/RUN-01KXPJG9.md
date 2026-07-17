# Decisions Ledger - RUN-01KXPJG9

> Append-only. One row per ruling; earlier rulings are never rewritten.

| At | Decision | Rationale |
| --- | --- | --- |
| 2026-07-17T02:55:39Z | Never run two tree-mutating verifiers concurrently: a TaskStop mid-mutant left conformance.py mutated, the second mutation run recorded baseline:fail (all 25 errors), and the full-diff critic reviewed the dirty tree. Recovery: checkout, re-verify, single-writer mutation re-run. | The mutation harness and any other verifier share one working tree; stopping the harness mid-mutant strands its mutant. Caught by the closing critic's tree-integrity check. |
