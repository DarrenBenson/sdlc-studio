# RFC-0013: the deploy last-mile, without ecosystem lock-in

> **Status:** Draft
> **Priority:** High
> **Author:** Darren Benson (from the v2.2 usage retrospective)
> **Date:** 2026-06-21
> **Spans:** sdlc-studio skill (a deploy workflow + verification oracle; reference-deploy-readiness.md, reference-config.md)
> **Related:** reference-deploy-readiness.md, templates/workflows/release-gate.md, CR0046 (the pre-deploy gate)
> **Supersedes / Superseded by:** --

## Summary

The skill is strong from PRD to **verified** code but stops there; "get quality code
**deployed**" - the verify -> deploy -> observe -> rollback last mile - is documented
patterns (`reference-deploy-readiness.md`), not a workflow. The design tension, and the
reason this is an RFC not a CR: a deploy capability must **not bake the skill into one
ecosystem** (GitHub Actions / AWS / k8s / a PaaS). The skill's ethos is that it owns the
*discipline*, the project owns the *runtime* (verify_ac invokes the project's own test
runners; autosprint wraps the project's own wave engine). Deploy should follow the same
rule.

## Context & Problem

`reference-deploy-readiness.md` describes cold-spawn, smoke budget, soak, rollback - as
prose. There is no `deploy` workflow that runs the pre-deploy gate, performs/orchestrates
the deploy, runs post-deploy verification, and handles rollback. But shipping that risks
ecosystem coupling: a "deploy" command that assumes `gh`/Actions, or a cloud SDK, fails
the moment a user is on GitLab, a bare VPS, an on-prem runner, or a different cloud.

## Goals / Non-Goals

**Goals**
- Define what "safely deployed" *means* as a checkable contract (pre-deploy gate +
  post-deploy verification tier + rollback trigger), reusing the existing verify/gate.
- Stay **ecosystem-neutral**: the project supplies the deploy/rollback commands; the
  skill never assumes a CI, cloud, or registry.
- Close the loop: post-deploy outcome recorded back into the artifact graph.

**Non-Goals**
- Becoming a deploy tool / CD platform. The skill orchestrates and verifies; the
  project's own tooling deploys.
- Touching secrets, credentials, or cloud APIs directly.

## Design Options

### Option A - Deploy contract + project-supplied hook (neutral)
The skill defines the **contract** (pre-deploy gate -> the configured deploy command ->
post-deploy verification tier -> rollback on failure) and delegates the *act* to a
project-configured command (`deploy.command`, `deploy.rollback`, `deploy.smoke` in
`.config.yaml`). Zero ecosystem assumption - works for Actions, GitLab, a shell script,
`kubectl`, `flyctl`, anything. **Pros:** neutral, fits the verify_ac/autosprint pattern.
**Cons:** the project must wire its own deploy command (no turnkey magic).

### Option B - Shipped adapters for common targets
Ship adapters (GitHub Actions, Docker, k8s, serverless, a PaaS or two). **Pros:**
turnkey. **Cons:** exactly the lock-in/maintenance burden to avoid; picks winners; ages
badly.

### Option C - Status quo (patterns only)
Keep `reference-deploy-readiness.md` as guidance, ship no workflow.

### Option D - Hybrid: A now, optional example adapters later
The neutral contract+hook (A) as the core; a few **optional** example wirings shipped as
`templates/` (not core code) so they can't couple the skill.

## Recommendation

**A, evolving to D.** Define the deploy contract + verification oracle and delegate the
runtime to a project-configured command - the skill owns "is it safe to ship and did the
ship succeed," never "how to ship to vendor X." Optional example wirings can follow as
templates. This answers the lock-in worry directly: a user not on GitHub configures their
own `deploy.command` and everything else (gate, smoke, soak, rollback signal) is identical.

## Open Decisions

| # | Decision | Options | Owner | Status |
| --- | --- | --- | --- | --- |
| D1 | Neutrality model | contract+hook (A) **[leaning]** / shipped adapters (B) / hybrid (D) | Operator | Open |
| D2 | Execute vs orchestrate | skill runs `deploy.command` / skill only gates+verifies around an operator-triggered deploy | Operator | Open |
| D3 | Mandatory post-deploy tier | smoke required / + soak / advisory only | Design | Open |
| D4 | Rollback | auto-rollback on smoke failure (run `deploy.rollback`) / surface the procedure for the operator | Operator | Open |
| D5 | Config surface | `deploy.{command,rollback,smoke,soak_minutes}` in `.config.yaml`; secrets stay out of scope | Design | Open |
| D6 | Feedback | record the deploy outcome to a deploy-readiness artifact / LATEST.md | Design | Open |

## Architecture Impact

| Layer | Impact | Change Type |
| --- | --- | --- |
| `deploy` workflow (reference + help) | new: gate -> deploy hook -> verify tier -> rollback | New |
| reference-config.md | `deploy.*` keys | Enhancement |
| reference-deploy-readiness.md | becomes the workflow's verification spec | Enhancement |
| templates/ (optional) | example wirings per ecosystem (non-core) | New |

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Ecosystem lock-in | Medium | High | Option A - never assume a runtime; project supplies the command |
| The skill executing a bad deploy | Medium | High | D2 lean orchestrate+verify; explicit operator confirm; rollback path |
| Secret handling creep | Low | High | Non-goal; secrets never touched, only a project command is invoked |

## Phased Plan / Workstreams

| WS | Workstream | Becomes | Depends on |
| --- | --- | --- | --- |
| WS1 | Deploy contract + `.config.yaml` `deploy.*` schema | CR (TBD) | D1, D5 |
| WS2 | `deploy` workflow (gate -> hook -> verify tier -> rollback) | CR (TBD) | WS1, D2-D4 |
| WS3 | Post-deploy outcome feedback into the artifact graph | CR (TBD) | WS2, D6 |
| WS4 | Optional example wirings as templates (non-core) | CR (TBD) | WS2 |

## Decision

> *Filled on acceptance.* Chosen option + rationale + the CRs spawned.

**Outcome:** TBD - for discussion (the lock-in question is the crux)
**Rationale:** TBD
**Spawned CRs:** TBD

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Darren Benson | Raised - the deploy last-mile, framed neutrality-first; for discussion before deciding |
