# CR-0173: Agentic triage workflow: status transitions, human sampling policy, triage quality metrics, noise controls

> **Status:** Complete
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic (v4 breakdown):** [EP0014](../epics/EP0014-agentic-triage-and-noise-control.md)
> **Priority:** High
> **Type:** Enhancement
> **Raised-by:** Lena Marsh (Product amigo)
> **Depends on:** CR0167, CR0169

## Summary

Make triage an explicit, agent-performable workflow: defined status transitions (for example
`inbox -> triaged -> in progress -> done -> closed`) with `triaged_by` recorded; a human
sampling policy in place of human gating; triage quality metrics captured over time; and
built-in noise controls on artefact creation.

## Motivation

Triage will be agentic: the human moves from gate to auditor, sampling rather than
approving. Today triage is implicit (an artefact goes from Proposed to Approved by operator
attention) and unrecorded (nothing says who triaged, or that triage happened at all). For a
team of agent writers, an untriaged inbox with no explicit state is where findings rot and
duplicates breed. Making triage a recorded transition gives the sampling human a defined
surface to audit, gives the separation-of-duties rule (CR0170) its trigger point, and gives
quality metrics a place to accrue. Identity is allocated at creation (RFC0024); triage is a
status transition, never an identity event.

## Scope

**In scope**

- **Status vocabulary:** an explicit `inbox` (or equivalent pre-triage) state per artefact
  type, and a `triaged` transition gated by `transition.py`, which records `triaged_by`
  (structured, CR0169) plus triage-assigned severity/priority alongside the raiser's.
- **Human sampling policy** (config-declared, `reference-config.md`):
  - all Critical severity items sampled;
  - a configurable percentage of the remainder;
  - any item where the triaging persona's severity disagrees with the raiser's.
  Sampled items are marked for human review; the human audits the triage, they do not
  re-perform it.
- **Triage quality metrics over time:** false positive rate (triaged-valid items later
  closed as invalid) and severity inflation (raiser severity vs triage severity vs closure
  severity), recorded in telemetry - these numbers are what justify the sampling rate.
- **Noise controls:**
  - individual artefacts required for Medium severity and above;
  - Low severity findings consolidated into themed CRs rather than filed singly;
  - a configurable cap on artefact creation per session, fail-loud when hit.
- Workflow documentation (`reference-cr.md`/`reference-bug.md` triage sections) and help.

**Out of scope**

- Assigning triage work to specific agents (orchestrator territory, CR0172 boundary).
- Authority rules beyond CR0170's raiser-not-triager.
- Auto-closing anything: triage can downgrade or consolidate, only humans or the closing
  workflow close.

## Acceptance Criteria

- [ ] New artefacts enter `inbox`; `transition.py` gates the `triaged` transition, requires
      structured `triaged_by`, and enforces CR0170 at the same moment.
- [ ] Sampling policy is config-driven; a test over a fixture batch shows: every Critical
      sampled, the configured percentage of the rest sampled (deterministic seed), every
      severity-disagreement sampled.
- [ ] False positive rate and severity inflation are computed from the ledger by a script
      (no hand counting) and surfaced in `status.py` or telemetry output.
- [ ] Noise controls enforced at creation: a Low-severity single-finding filing is redirected
      to consolidation; the session cap refuses the N+1th artefact loudly.
- [ ] End-to-end dogfood: one real review batch (e.g. from CR0175) flows inbox to triaged
      under the policy, with sampling marks visible in the ledger.

## Dependencies

| Artefact | Relationship |
| --- | --- |
| CR0167 | Blocking: pre-triage artefacts must already have stable ids to be cross-referenced (decided: identity at creation) |
| CR0169 | Blocking: `triaged_by` is a structured reference |
| CR0170 | Enforced at the triage transition this CR introduces |
| CR0171 | Evidence fields feed the false-positive metric |
| CR0175 | First large-scale producer of triage inflow; natural dogfood pairing |

## Effort

**L.** Status vocabulary across types, transition gating, config, sampling logic, metrics,
noise controls, and docs.

## Risk

The gate-to-auditor shift fails socially, not technically, if sampling is silently skipped:
the human believes triage is audited when nobody looks. Mitigation: sampled-but-unreviewed
items are visible drift in `status.py` (a standing count, not a one-time prompt), and the
metrics exist precisely to show whether agentic triage is earning its autonomy.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Lena Marsh (Product amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Lena Marsh (Product amigo) | Full scope drafted; gate-to-auditor policy and noise controls specified |
