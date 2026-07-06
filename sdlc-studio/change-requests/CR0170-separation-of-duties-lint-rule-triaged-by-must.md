# CR-0170: Separation of duties lint rule: triaged_by must not equal raised_by

> **Status:** Proposed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Enhancement
> **Raised-by:** Sam Eriksson (QA amigo)
> **Depends on:** CR0169

## Summary

A lint rule enforcing `triaged_by != raised_by` on every triaged artefact. This is the
minimal viable permission rule implementable with personas today: the adversarial-review
pattern compiled into a lint check.

## Motivation

The skill already lives by "the seat that wrote the tests never signs them off" (Sam's
non-negotiable), "never the same instance for both on one unit" (every amigo's dual-render
rule), and the RFC0020 independence gate. Those are prose conventions enforced by discipline.
As triage becomes agentic (CR0173) and writers multiply, discipline does not scale but a lint
does. With structured authorship (CR0169) the rule becomes a one-line comparison over typed
fields rather than string matching on free text.

Broader authority matrices (who may raise what, who may approve what) are explicitly out of
scope for this version - a decided boundary, recorded here so reviewers do not re-open it on
this CR.

## Scope

**In scope**

- Lint rule: any artefact with a `triaged_by` block where it deep-equals `raised_by`
  (same `name` and `type`) fails, naming both fields and the artefact.
- Wired into `validate.py`, the consolidated lint (CR0174), and the portable `gate.py`.
- `transition.py` refuses the triage transition when the acting identity equals `raised_by`
  (fail at write time, not just at CI time).
- Persona-instance nuance documented: two instances of the same persona are still the same
  `name`, so they fail the rule; that is intended (the RFC0021 seats model already requires
  distinct seats, not distinct instances).

**Out of scope**

- Authority matrices, role permissions, or any rule beyond raiser-not-triager (deferred past
  this version by decided boundary).
- Cryptographic identity or spoof-resistance; a lying writer defeats any frontmatter rule,
  and that threat model is later agentic-entity work.

## Acceptance Criteria

- [ ] A fixture artefact with identical raiser and triager fails `validate.py`, the
      consolidated lint, and `gate.py`, each naming the rule.
- [ ] `transition.py` rejects a triage transition where the actor equals `raised_by`, with a
      message telling the caller to hand off to a different seat.
- [ ] Distinct personas pass; same persona different instance fails (test both).
- [ ] Untriaged artefacts (no `triaged_by` yet) pass untouched; the rule fires only once
      triage is recorded.
- [ ] Rule is documented as a worked example in the consolidated lint docs (CR0174).

## Dependencies

| Artefact | Relationship |
| --- | --- |
| CR0169 | Blocking: the rule compares fields CR0169 introduces |
| CR0173 | Consumer: agentic triage records the `triaged_by` this rule checks |
| CR0174 | The consolidated lint is this rule's CI home |

## Effort

**S.** A comparison, two enforcement points, tests, and docs.

## Risk

Low. The one failure mode worth naming: a solo human operator with no personas configured
would deadlock (they raised everything, so they can triage nothing). The rule must therefore
treat `type: human` self-triage as a warning, not an error, until a second identity exists -
solo-first is still the primary team shape.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Full scope drafted; solo-human warning carve-out noted |
