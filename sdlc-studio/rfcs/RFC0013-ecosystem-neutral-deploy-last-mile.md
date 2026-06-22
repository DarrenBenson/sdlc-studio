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

**A, orchestrate-only - and defer the build until the trigger fires.** Refined after the
2026-06-22 pressure-test (below). Define the deploy **contract + verification oracle** and have
the skill **gate, verify, and record around an operator-triggered deploy** - it owns "is it safe
to ship, and did the ship succeed," and it never holds the production trigger, never auto-rolls-back,
and never runs inside an autonomous loop. The read-only gate half is the honest analogue of
`verify_ac`; the act half (execute / rollback) is where lock-in, blast-radius, and false-neutrality
live, so the skill orchestrates around it rather than performing it. Drop the "evolving to B-style
adapters" framing; if examples are ever needed they are illustrative snippets in the reference, not a
maintained per-ecosystem adapter surface. **Build is deferred:** the skill's live consuming projects
already deploy with their own `deploy.sh` / `rollback.sh` / `smoke.sh`, so the trigger - "a project
needs the skill to *sequence and gate* a deploy it cannot already sequence itself" - is unmet.

## Pressure-test (2026-06-22)

Four independent adversarial lenses (RFC0016 isolated-seat model) attacked the original "A->D"
recommendation. Convergent findings:

- **The value is the contract, not the execution (~80%).** A pre-deploy gate that refuses to ship
  unverified code + a post-deploy verification oracle (smoke / soak) + a rollback *trigger* + the
  outcome recorded back (D6). Running `deploy.command` is the commodity part every CI already does.
  Sell "refuses to let unverified code ship and proves the ship worked, around whatever deploy you
  already have" - not "let the skill deploy for you."
- **The `verify_ac` analogy holds for the gate, breaks for the act.** Verify is read-only,
  idempotent, local; deploy is stateful, irreversible, credentialed, networked. The four-key contract
  silently assumes a *reachable, reversible, single-shot, locally-observable* deployment (a 12-factor
  world) - itself an ecosystem. Keep the contract honest about the read-only half.
- **Safety:** deploy is a stop-condition (c) action; an autosprint triage approval must **not**
  transitively authorise a prod rollout. Deploy is a separate, explicitly operator-invoked step the
  loop can prepare up to (gate green, artefact ready) and **hand back** - never trigger. Agent
  auto-rollback is unsafe (cannot tell a flaky / cold-spawn smoke failure from a real one, cannot
  reverse a forward migration, cannot reason about partial state).
- **Timing:** the consumers already own deploy tooling - building now is ceremony over scripts they
  trust. WS3 (feedback plumbing) and WS4 (example adapters) are the most wasteful / most
  lock-in-prone parts; exclude them. MVS, only when triggered, = WS1+WS2 collapsed, orchestrate-only.
- **The adapter tail (D) split the lenses** (neutrality: kill it - "non-core" is an unenforceable
  fiction; adoption: needed so users know what to put in `deploy.command` / `rollback`). Resolved:
  illustrative snippets in the reference doc at build time, never a maintained adapter file set.

## Open Decisions

| # | Decision | Resolution (2026-06-22 pressure-test) | Owner | Status |
| --- | --- | --- | --- | --- |
| D1 | Neutrality model | **A (contract+hook), orchestrate-only subset.** Kill B; the D adapter tail becomes illustrative snippets at build time, never maintained adapter files | Operator | Decided |
| D2 | Execute vs orchestrate | **Orchestrate.** Skill gates + verifies + records around an operator-triggered deploy; it never holds the production trigger | Operator | Decided |
| D3 | Mandatory post-deploy tier | **Smoke required** to call a deploy *rolled out*; **soak required** to call it *verified / Done*. Smoke-green alone is never "verified" | Design | Decided |
| D4 | Rollback | **Surface the procedure; the agent never auto-fires `deploy.rollback`.** A project's own deploy script may self-rollback internally | Operator | Decided |
| D5 | Config surface | `deploy.{command (optional), smoke, soak_minutes}` + `deploy.rollback` as a documented *procedure*; one command is not assumed sufficient; secrets out of scope | Design | Decided |
| D6 | Feedback | **Record the outcome** (rolled-out / verified + smoke/soak results) to LATEST.md / a deploy-readiness note - part of the contract's value | Design | Decided |
| D7 | Autonomy | **Deploy never runs inside autosprint's autonomous loop.** It is a stop-condition (c) hard pause that does not inherit triage approval | Operator | Decided |

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

**Outcome:** Design **settled** (Option A, orchestrate-only) and **build deferred.** The pressure-test
resolved D1-D7; the recommendation is sharpened from "A -> D, execute" to "A orchestrate-only - no
auto-execute, no auto-rollback, never in the autonomous loop." No CRs spawned now.
**Rationale:** the value is the read-only contract (pre-deploy gate, post-deploy verification oracle,
rollback trigger, recorded outcome), which is honestly ecosystem-neutral; the execute/rollback half
smuggles topology assumptions and production blast-radius, so the skill orchestrates around it rather
than performing it. Both live consumers already own their deploy tooling, so the build trigger is
unmet - building now would be ceremony over scripts they already trust.
**Trigger to build:** a consuming project needs the skill to *sequence and gate* a deploy it cannot
already sequence itself. MVS then = WS1+WS2 collapsed into one CR, orchestrate-only, excluding WS3
(feedback plumbing) and WS4 (example adapters).
**Spawned CRs:** none (deferred).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Darren Benson | Raised - the deploy last-mile, framed neutrality-first; for discussion before deciding |
| 2026-06-21 | Darren Benson | Decision session: DEFERRED (stays Draft) - needs the most thought + no live deploy need. Trigger: a consuming project needs a coordinated, gated deploy (the lock-in question reopens then) |
| 2026-06-22 | Pressure-test (4 adversarial lenses) | Design settled: A orchestrate-only (no auto-execute / no auto-rollback / never in the autonomous loop); D1-D7 decided; B and the adapter tail killed; build remains deferred until the trigger fires. MVS scoped to WS1+WS2 |
