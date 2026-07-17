# RV0012 – Sprint-close review – the audit-backlog sprint (RUN-01KXQH64)

> **Review type:** Sprint-close (CODE leg = adversarial full-diff critic pass; document legs assessed for currency)
> **Reviewer:** QA seat, independent worktree-isolated critic, full-diff refute framing (required a run reproduction per claim)
> **Date:** 2026-07-17
> **Triggered by:** the RUN-01KXQH64 close (mandatory reconcile + review)
> **Scope:** git diff 96bbaa4..HEAD - 29 delivered bugs (BG0152-BG0181), the 2026-07-16 adversarial-audit backlog
> **Predecessor:** RV0011 (sprint-close, RUN-01KXPJG9, 2026-07-17); standing unified picture RV0010 (2026-07-16)

## Headline

The 2026-07-16 audit backlog cleared 29/29. Cluster A (the cost/measurement machinery -
telemetry/retro/config) was author-driven and test-first; clusters B, C and the loose bugs
ran as three parallel isolated-worktree subagents and merged conflict-free (file-disjoint,
scope verified per commit). The closing full-diff pass found ONE MAJOR regression the fixing
unit's own test was too narrow to catch, repaired test-first and re-verified against the
reviewer's exact reproduction before APPROVE.

## CODE leg (the sprint diff)

- Verdict: **APPROVE** after one repair round. The independent critic tried hardest to break the
  cluster-A cost aggregation (double-count on reopen-reclose/bare-close, flat-vs-attempts
  disagreement, model-only records), the majority elapsed-match boundary, the pricing raw-id
  resolution, and the fail-closed paths (BG0155/0167/0180/0154) - all reproduced as sound.
- **MAJOR, repaired:** BG0181's first fix truncated the batch line at the first `(`, silently
  dropping delivery units listed after an inline provenance parenthetical (repro: RETRO0006 -> 3 of
  8 units). Fixed to strip each `(...)` in place, with a mid-line regression test; re-verified by
  re-running the reviewer's RETRO0006 repro (now 8/8). Committed 3eab402.
- **MINOR, accepted by design:** mixed-model units count in the batch total but not the per-model
  rows, so those rows do not sum to the batch total - correct (a mixed unit's tokens cannot be
  booked to one model), no code asserts the reconciliation.
- Mutation evidence: a bounded run (baseline pass) was recorded but uninformative - the low ceiling
  sampled peripheral git/path helpers, not the changed cost code (10/826). The assurance is the
  TDD-red-first tests and the adversarial pass, recorded honestly rather than dressed up. Follow-up
  CR0336 (surface the refused state) filed.
- Gate: PASS end-to-end (style, links, versions, budgets, neutrality, action-pins, conformance /
  reconcile / validate / integrity / duplicate-id / docs, skill-tests, tool-tests, markdown).

## Document legs

- **PRD/TRD/TSD:** this sprint DID touch them - the spec-rot half of the audit backlog. BG0156
  (PRD telemetry data model), BG0157 (PRD+TRD breakdown-gate sizing), BG0168 (PRD+epic status),
  BG0162/0170 (TSD test-coverage + gate-lane tables), BG0154 (TRD writer list) each corrected a
  document-of-record to match the shipped behaviour. The remaining RV0010 synthesis debt is now
  materially reduced; what stands is the residual audit CRs (CR0280-CR0306) not in this bug batch.
- **Personas:** the QA seat carried the closing review; seat cards unchanged.
- **New documents of record:** `help/audit.md` (the `audit` command, previously catalogued
  nowhere).

## Sprint Goal verdict

"Clear the 2026-07-16 audit backlog so the sprint machinery (telemetry, retro, gate) and the
documents of record (PRD/TRD/TSD) match the shipped behaviour." - **ACHIEVED**: all 29 bugs
delivered (delivery backlog 0 open), the telemetry/retro cost machinery now reads one honest
attempts-first cost across readers, the gate/close-down/eval/mutation fail-closed paths were
proven under adversarial repro, and the PRD/TRD/TSD spec-rot the audit named was corrected in the
same batch.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | Claude Opus 4.8 | Sprint-close review recorded |
