# SDLC Studio Reference - Deploy (the orchestrate-only last-mile)

<!-- Load when: /sdlc-studio deploy - gating, verifying, and recording a deploy without owning the runtime -->

Deep workflow for `/sdlc-studio deploy` (RFC0013). The skill carries the project from PRD to
**verified** code; `deploy` carries it the last mile to **shipped** - without baking the skill into
any ecosystem. It **gates** before a deploy and helps **verify** and **record** after it. It never
holds the production trigger, never auto-rolls-back, and never deploys inside the autonomous loop.

## The contract (what "safely deployed" means)

`deploy` is a checkable contract, not a deploy tool:

1. **Pre-deploy gate** - the same quality gate (`/sdlc-studio gate`) must be green. Unverified code
   does not ship.
2. **Operator-triggered deploy** - the project's own `deploy.command` (any ecosystem) performs the
   act. The skill **hands off** the command; the operator runs it. The skill never holds the trigger.
3. **Post-deploy verification oracle** - `deploy.smoke` (a `verify_ac` expression) confirms the ship.
   **Smoke green == "rolled out"; a `deploy.soak_minutes` soak window must pass before "verified"
   (Done).** Smoke alone is never "verified".
4. **Rollback as a surfaced procedure** - on a failed smoke, the skill surfaces `deploy.rollback`
   (steps or a hand-run command). The agent never fires it - it cannot tell a flaky/cold-spawn smoke
   failure from a real one, reverse a forward migration, or reason about partial state.
5. **Recorded outcome** - the result (rolled-out / verified / rolled-back / failed) is appended to
   `sdlc-studio/deploy-log.md`, closing the last mile back into the artifact graph.

Ecosystem-neutral by construction: the project supplies the commands in `.config.yaml`
(`reference-config.md#deploy`); the skill assumes no CI, cloud, or registry, and never reads secrets.
With no `deploy.*` configured, `deploy` is a pure gate + verification harness around a deploy you
trigger yourself.

## Safety - deploy is never autonomous

Deploy is a stop-condition (hard-to-reverse) action. **It must not run inside `autosprint`** and an
autosprint triage approval must **not** transitively authorise a production rollout. The loop may
prepare up to "gate green, artefact ready" and **hand back**; the operator runs `deploy` explicitly
and interactively. The skill's role is to *gate, hand off, verify, and record* - never to execute the
deploy or the rollback.

## Workflow {#deploy-workflow}

```text
1. preflight  - python3 "$CLAUDE_SKILL_DIR/scripts/deploy.py" preflight
                -> runs the gate; READY only if green. Prints the operator hand-off:
                   the deploy command to run + the rollback procedure to keep ready.
2. (operator) - run the deploy out-of-band (deploy.command, or your own pipeline).
3. smoke      - run deploy.smoke (a verify_ac expression). Green => rolled out.
4. soak       - wait deploy.soak_minutes; re-check. Stable => verified.
5. on failure - surface deploy.rollback for the operator (the agent does not run it).
6. record     - python3 "$CLAUDE_SKILL_DIR/scripts/deploy.py" record --status <s> --detail "..."
                where <s> = rolled-out | verified | rolled-back | failed
```

## The helper

`scripts/deploy.py` provides the deterministic, read-only pieces (it never deploys):

- `deploy.py preflight [--format json]` - reads `deploy.*`, runs the gate, emits the readiness verdict
  and the operator hand-off. Exit 0 when ready (gate green), 1 otherwise.
- `deploy.py record --status <rolled-out|verified|rolled-back|failed> [--detail "..."]` - appends a
  timestamped row to `sdlc-studio/deploy-log.md` (WS3 - the outcome feedback).

## See also

- `reference-config.md#deploy` - the `deploy.*` schema
- `reference-deploy-readiness.md` - cold-spawn, smoke budget, soak, rollback patterns (the
  verification spec this workflow runs against)
- `templates/workflows/release-gate.md` - the human-readable pre-release checklist
