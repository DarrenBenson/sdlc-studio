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
| `deploy.py metrics` | The DORA four keys from records already kept: deployment frequency + change failure rate (the ledger), lead time (git author times between deploy events), MTTR (High/Critical bugs Created -> Fixed). Advisory - no key feeds a gate; an absent source is named UNMEASURABLE; no ledger = not applicable, never a nag |
| `escape.py failure-rate [--since D] [--until D] [--settle-days N]` | Change failure rate from records: the releases with at least one linked incident over the releases counted. `--since`/`--until` set the window (default the 90 days ending today, both days included); a release younger than `--settle-days` (default 14) at the window's end, or today if earlier, is pending and counted neither way, even when an incident names it. Its sources are the release records `release_cut.py changelog-cut` writes and incidents, issues whose `## Root Cause` section is written, linked through the escaped bugs they were triaged into. No release record or no incident reads not measured, never 0%. Where `deploy.py metrics` counts `failed` and `rolled-back` rows of the deploy ledger, this counts releases with a linked incident; the sprint report's DORA row counts CI push runs. Advisory, as `deploy.py metrics` is |

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
