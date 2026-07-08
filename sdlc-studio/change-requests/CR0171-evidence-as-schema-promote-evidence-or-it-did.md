# CR-0171: Evidence as schema: promote evidence-or-it-did-not-happen to lint-enforced structure

> **Status:** Complete
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic (v4 breakdown):** [EP0013](../epics/EP0013-structured-authorship-and-policy-enforcement.md)
> **Priority:** Medium
> **Type:** Enhancement
> **Raised-by:** Sam Eriksson (QA amigo)
> **Depends on:** CR0169

## Summary

Promote the evidence-or-it-did-not-happen rule from convention to required frontmatter or
sections per artefact type: file and line references, command output, or reproduction steps
as appropriate for bugs; impact statement and effort estimate for CRs. Lint-enforced.

## Motivation

Evidence discipline is the core of the anti-vibe-coding stance (files over chat, evidence
over intent), but today it is convention plus reviewer vigilance. In the target team shape -
agentic triage, many agent writers, a human who samples rather than gates (CR0173) - the
sampler needs artefacts whose evidence is machine-checkably present before quality can even
be assessed. A bug without a reproduction is not a smaller bug report; it is a rumour. An
evidence schema also feeds triage quality metrics: false-positive rate is only measurable
when every finding states what would prove it.

## Scope

**In scope**

- Per-type required evidence, enforced by lint:
  - **Bug:** at least one of file-and-line reference, command output, or reproduction steps;
    severity justification line.
  - **CR:** impact statement (who is affected and how) and an effort estimate.
  - **RFC:** at least two weighed options (the template demands it; the lint now checks it).
- Presence and shape checks only: the lint verifies a section exists and is non-placeholder
  (no `{{...}}`, non-empty), not that the evidence is true - truth stays with reviewers and
  `verify_ac.py`.
- `artifact.py` scaffolds updated so the required sections are pre-seeded per type.
- Rule wired into `validate.py`, the consolidated lint (CR0174), and `gate.py`.
- Grace policy for pre-schema-v3 artefacts: legacy artefacts are exempt; the rule applies
  from schema v3 creation date onward.

**Out of scope**

- Judging evidence quality or verifying claims (that is `verify_ac.py`, reviews, and the
  critic).
- New evidence types for stories/epics (their Ready gates already carry AC discipline).
- Retroactive rewriting of closed artefacts to add evidence they never had - the audit trail
  stays honest about its era.

## Acceptance Criteria

- [ ] A bug with no file reference, no command output, and no reproduction steps fails the
      lint with a message naming the three accepted evidence forms.
- [ ] A CR without an impact statement or without an effort estimate fails the lint.
- [ ] Placeholder text (`{{...}}` or empty section) counts as absent (test each type).
- [ ] Legacy artefacts predating schema v3 pass untouched (era-gating test).
- [ ] `artifact.py new --type bug` scaffold contains the evidence section stubs so the happy
      path writes evidence where the lint will look for it.

## Dependencies

| Artefact | Relationship |
| --- | --- |
| CR0169 | Blocking: era-gating and per-type rules key off the schema-v3 frontmatter CR0169 lands |
| CR0173 | Consumer: noise controls and triage metrics assume evidence fields exist |
| CR0174 | The consolidated lint is this rule's CI home |

## Effort

**M.** Rule table per type, placeholder detection, scaffold updates, era gating, tests.

## Risk

Over-strict presence checks would push agents into writing filler evidence to satisfy the
lint - worse than absence because it looks like evidence (LL0009: silent misleading beats
loud failure in severity). Mitigation: placeholder detection plus the CR0173 sampling policy
explicitly samples for filler evidence.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Full scope drafted; presence-not-truth boundary stated |
| 2026-07-08 | sweep-close (backlog reconciliation) | Delivered via US0062, already Done; CR status was never cascaded to Complete -> closed |
