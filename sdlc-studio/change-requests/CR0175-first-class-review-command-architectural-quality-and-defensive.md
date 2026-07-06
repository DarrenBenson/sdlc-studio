# CR-0175: First-class review command: architectural, quality and defensive security review of the host repo

> **Status:** Proposed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Type:** Enhancement
> **Raised-by:** Sam Eriksson (QA amigo)
> **Depends on:** none blocking (soft: CR0173 triage rules once available)

## Summary

A `review generate` (or `audit`) command that performs an architectural, code quality, and
defensive security review of the host repo, producing a dated report in `reviews/` and
triaging findings into bugs and CRs under the CR0173 rules.

## Motivation

This is the lowest-commitment on-ramp to the tool: review is how someone tries sdlc-studio
on an existing repo before adopting the full pipeline. Point it at code you already have,
get a report and a triaged set of findings, and you have experienced files-over-chat and
evidence-over-intent without committing to a PRD or a single epic. Every other entry point
asks for adoption first and pays off later; this one pays off in the first hour.

Distinct from what exists: `/sdlc-studio review` today reviews the project's own artefacts
(PRD/TRD/TSD/personas), and `audit` (RFC0002) hunts weaknesses in the artefact graph. This
command reviews the host repo's code. A complete hand-written prompt for this workflow
already exists and should be attached to this CR as the starting specification when it is
actioned.

## Scope

**In scope**

- Command producing a dated report in `reviews/` (fits the existing `RV{NNNN}` convention)
  covering three legs: architecture, code quality, defensive security (LL0005: a review set
  must include a code leg - this command is that leg, generalised).
- Findings triaged into bugs and CRs via `file_finding.py` under the CR0173 noise rules
  (Medium+ individual, Low consolidated, session cap) once those ship; until then, under
  current filing conventions.
- **Security findings are remediation-only by design: location, weakness class, impact, and
  fix; no proof-of-concept exploits or payloads; secret values never copied into artefacts,
  only locations plus rotation instructions.** This wording keeps the command runnable under
  current frontier model policies and must be preserved verbatim in the command's prompt
  template.
- Works on a repo with no sdlc-studio workspace: bootstraps the minimal folders it needs
  (reviews/, bugs/, change-requests/) without demanding `init` or a PRD first - the on-ramp
  property depends on this.
- Help file, reference section, and README mention as the try-it-first command (consumed by
  CR0177).

**Out of scope**

- Penetration testing, exploit development, or dynamic analysis; this is a static,
  remediation-oriented review.
- Reviewing artefact quality (existing `review`) or the artefact graph (existing `audit`);
  this CR neither replaces nor absorbs them.
- CI integration of the review itself (the produced findings flow into normal gates).

## Acceptance Criteria

- [ ] Running the command on a repo with no sdlc-studio workspace produces a dated
      `reviews/RV*` report plus filed findings, with no prerequisite steps.
- [ ] The report has the three legs (architecture, quality, defensive security) with
      file-and-line evidence per finding (CR0171-shaped even before that lint lands).
- [ ] The security-findings policy paragraph appears verbatim in the prompt template, and a
      test asserts its presence (guard against silent edits).
- [ ] A fixture repo with a planted hard-coded secret yields a finding giving location and
      rotation instructions with the secret value absent from every produced artefact
      (test greps outputs for the planted value).
- [ ] Findings flow through triage: severity recorded, Low findings consolidated, individual
      artefacts for Medium+ (full CR0173 behaviour once shipped; current conventions until).
- [ ] The existing hand-written review prompt is attached as the starting specification and
      its deltas from the shipped template recorded.

## Dependencies

| Artefact | Relationship |
| --- | --- |
| CR0173 | Soft: this command is the natural producer for agentic triage; runnable before it under current conventions |
| CR0171 | Soft: evidence schema formalises the finding shape this command already emits |
| CR0177 | Consumer: README positions review as the on-ramp |

## Effort

**M.** The prompt exists; the work is command wiring, workspace bootstrap, the
secret-handling guard test, and filing integration.

## Risk

A weak first review is a weak first impression - the on-ramp cuts both ways. Mitigation: the
existing hand-written prompt is field-tested, and the noise controls stop a finding flood
from burying the three that matter. The security-policy wording is load-bearing for
runnability; the verbatim-presence test exists so a well-meaning edit cannot quietly break
the command on frontier models.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Full scope drafted; on-ramp framing and verbatim security policy pinned |
