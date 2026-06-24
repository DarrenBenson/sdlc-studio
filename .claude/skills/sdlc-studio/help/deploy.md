# Help: deploy

<!-- Load when: /sdlc-studio deploy - the orchestrate-only deploy last-mile -->

## You can just ask

SDLC Studio is model-invoked - say it in plain language:

| Just say... | Runs |
| --- | --- |
| "Is it safe to ship this?" | `/sdlc-studio deploy` (preflight gate) |
| "Walk me through the release" | `/sdlc-studio deploy` |
| "Check we're ready, then hand it to me" | `deploy.py preflight` |
| "The deploy went out and smoke is green" | `deploy.py record --status rolled-out` |
| "It's soaked clean, mark it verified" | `deploy.py record --status verified` |
| "We had to roll back" | `deploy.py record --status rolled-back` |

Gate, verify, and record a deploy **without owning the runtime**. The skill never holds the
production trigger, never auto-rolls-back, and **never deploys inside `sprint`** - the deploy is
operator-triggered and interactive. With no `deploy.*` configured it is a pure gate + verification
harness around a deploy you run yourself.

## Commands

| Command | What it does |
| --- | --- |
| `/sdlc-studio deploy` | Run the workflow: preflight (gate) -> operator hand-off -> smoke/soak verify -> surface rollback on failure -> record outcome |
| `deploy.py preflight` | Gate + readiness verdict + the operator hand-off (no deploy). Exit 0 if ready |
| `deploy.py record --status <s> --detail "..."` | Append an outcome (`rolled-out`/`verified`/`rolled-back`/`failed`) to `sdlc-studio/deploy-log.md` |

## Prerequisites

- A green quality gate (`/sdlc-studio gate`). Unverified code does not ship.
- Optionally, `deploy.*` in `.config.yaml` (`command`, `smoke`, `soak_minutes`, `rollback`) - see
  `reference-config.md#deploy`.

## Contract

Smoke green == **rolled out**; a `soak_minutes` window must pass before **verified** (Done). Rollback
is a surfaced **procedure**, never auto-run by the agent.

## Examples

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/deploy.py" preflight              # is it safe to ship? + hand-off
# (operator runs the deploy out-of-band, then verifies smoke)
python3 "$CLAUDE_SKILL_DIR/scripts/deploy.py" record --status verified --detail "v1.4.0, soak clean"
```

See `reference-deploy.md` for the full workflow and `reference-deploy-readiness.md` for the
verification patterns.
