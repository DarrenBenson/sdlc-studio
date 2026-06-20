# RFC-0003: Promote reconcile's mechanical apply into the script; current Phase-3 apply is prose and the documented idempotency guarantee is false

> **Status:** Accepted
> **Priority:** High
> **Author:** Adversarial Audit
> **Date:** 2026-06-20
> **Spans:** sdlc-studio skill
> **Related:** RV0002 (audit run)
> **Supersedes / Superseded by:** --

## Summary

reconcile.py is detect-only (four drift classes); the entire Phase-3 apply - ticking checkboxes, rewriting dependency-table Status cells, recomputing summary counts, the Story/Epic completion cascades - is done by Claude in prose, contradicting the documented 'Idempotent' guarantee and accruing the stale-artifact backlog LL0001 catalogued.

## Context & Problem

reconcile.py is explicitly read-only and emits drift for only status-mismatch, missing-row, orphan-row, count-mismatch (reconcile.py:129-205). Every other Phase-2 check (epic story-breakdown checkbox drift, epic/story dependency-table drift, PRD feature-status drift, numeric-claim drift, reference-reconcile.md:104-162) and the whole of Phase-3 apply (reference-reconcile.md:211-246) plus the Story (12-step) and Epic (9-step) completion cascades (reference-outputs.md:647-713) are applied by Claude by hand. These edits are mechanical (find row -> set cell; find '- [ ]' -> '- [x]'; count files -> write count). reference-reconcile.md:270 nonetheless asserts reconcile is 'Idempotent - running reconcile twice produces the same result', a property a deterministic script provides but a prose LLM apply does not; LL0001 found 15 stale index rows, 82+ unchecked boxes, and 14 stale dependency refs that prose passes had missed.

## Design Options

### Option A - act on the finding

Promote the mechanical apply into reconcile.py behind an explicit 'apply' subcommand with a --dry-run contract: rewrite index Status cells from the file census, recompute summary counts by enumeration, tick story-breakdown/AC checkboxes from the truth map, and rewrite dependency-table Status columns by ID lookup. Keep genuinely judgemental items (CR completion, PRD prose) report-only. The aim is an apply that round-trips through the same census reconcile already builds, so that idempotency can be made a tested property of the script rather than an asserted one - any such guarantee would need round-trip idempotency tests to back it. RFC because it converts a read-only tool into a file-mutating one needing those idempotency tests and a dry-run contract.

### Option B - status quo

Keep the current behaviour and accept the trade-off described above.

## Recommendation

TBD - pending the Open Decision below.

## Open Decisions

| # | Decision | Options | Owner | How it resolves | Status |
| --- | --- | --- | --- | --- | --- |
| D1 | Act on this finding or keep status quo | Option A / Option B | Operator | spike or operator call | Resolved |

## Evidence

reference-reconcile.md:270 (claims idempotency) vs reconcile.py:8-10 ('Read-only: emits a JSON report; Claude ... does the editing') and reference-outputs.md:687 (records the 15/82+/14 stale-artifact backlog prose accrued)

## Impact

The largest token cost and largest drift-correctness risk in the skill: every reconcile and every story/epic close re-derives mechanical edits by hand (~3-4k tokens each, repeated per cadence trigger) and misses some, leaving stale dashboards, dependency tables, and PRD statuses. The documented idempotency guarantee is currently false. Quality risk high.

## Decision

**Outcome:** Accepted (Option A, scoped)

**Rationale:** Highest value (removes the biggest token cost + drift risk) but highest corruption risk, so the dry-run contract + round-trip idempotency tests are non-negotiable scope.

**Spawned CRs:** One CR: reconcile `apply` subcommand behind --dry-run, mechanical classes only (index Status cells, counts, AC checkboxes, dependency Status), idempotency tests in the same CR; CR-completion + PRD prose stay report-only. Created when picked up.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (rfc-decide session) | Accepted in the RFC decision session - Accepted (Option A, scoped) |
| 2026-06-20 | Adversarial Audit | Filed from the 2026-06-20 audit (lens: determinism) |
