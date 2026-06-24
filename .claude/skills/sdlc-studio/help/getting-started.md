<!--
Load when: starting a greenfield project, or asking "what order do I run things in?"
Dependencies: SKILL.md (always loaded first)
Related: help/init.md, reference-verify.md, reference-sprint.md, reference-scripts.md
-->

# Greenfield Runbook - From Empty Repo to Shipped

## You can just ask

SDLC Studio is model-invoked - say it in plain language:

| Just say... | Runs |
| --- | --- |
| "Set up a brand new project here" | `/sdlc-studio init --scaffold` |
| "Draft the product requirements" | `/sdlc-studio prd` |
| "Break the PRD into epics" | `/sdlc-studio epic` |
| "Write the stories for this epic" | `/sdlc-studio story --epic EPxx` |
| "Check the backlog is wired and clean" | `/sdlc-studio reconcile` then `validate` |
| "Take this epic to done on its own" | `/sdlc-studio sprint --epic EPxx --goal done` |

The canonical command order for a new project, start to a reviewable backlog and on through
the implementation handoff. Each step: why, the command, what it produces, what it unblocks.
You do not reconstruct this from scattered "Next steps" footers - it is the path.

## 1. Authoring - PRD to a reviewable backlog

| # | Step | Command | Produces / unblocks |
| --- | --- | --- | --- |
| 1 | **Bootstrap** | `init [--detect] [--scaffold]` | the full `sdlc-studio/` tree, every `_index.md`, config, `AGENTS.md`/`CLAUDE.md`. After this the first `new` of any type is indexed. `--scaffold` also seeds `prd`/`trd`/`tsd`/`personas`. |
| 2 | **Product requirements** | `/sdlc-studio prd` | `prd.md` - features, NFRs, open questions |
| 3 | **Personas** | `/sdlc-studio persona` | `personas.md` - the cast stories are written for |
| 4 | **Technical + test design** | `/sdlc-studio trd` then `tsd` | `trd.md`, `tsd.md` - architecture + the test strategy |
| 5 | **Epics** | `/sdlc-studio epic` | epics from the PRD (decompose the feature set) |
| 6 | **Stories** | `/sdlc-studio story --epic EPxx` | Ready stories with Given/When/Then + DSL `Verify:` lines. For many at once, `artifact.py batch` reserves a contiguous id block and wires them in one pass. |
| 7 | **Reconcile + validate** | `/sdlc-studio reconcile` then `validate` | a wired, drift-free, reviewable backlog |

Record load-bearing decisions as they land with `decisions.py add` (the project spine -
product decisions and implementation conventions; resolved PRD open questions are promoted
in with `decisions.py promote --from PRD-OQn`). Delegated authoring agents read it as their
handoff context.

> **Authoring loop:** a single guarded loop can collapse steps 5-7 - drive the PRD to a
> reviewable backlog, pausing to approve the epic cut and resolve open questions, then stop.
> Where it is not available, run the steps above in order.

## 2. Implementation - the sprint handoff

**sprint needs a runnable verification environment.** Its loop (implement -> test ->
gate -> critic -> commit-green) leans on a gate it can actually run each iteration. On
greenfield that does not exist yet, so:

1. **Build the foundation epic by hand to a green gate.** It establishes the buildable /
   testable scaffold (toolchain, test harness - an in-memory substitute like `pg-mem` is
   enough; the gate need only *run*) and the high-judgement conventions every later story
   inherits (error-envelope shape, ID scheme, migration strategy). Commit it green.
2. **Then hand subsequent epics to sprint:** `sprint --epic EPxx --goal done`. Now
   there are working tests and a gate for the loop to lean on.

> **Rule: do not invoke sprint before the quality gate is runnable and green.**

## See Also

- `help/init.md` - the bootstrap step in detail
- `reference-verify.md` - the test-spec AC-to-test bridge + the `Verify:` DSL
- `reference-sprint.md` - the autonomous delivery loop (and its cold-start precondition)
