# Benchmark protocol (pre-registered)

> **Status:** pre-registered · **Date:** 2026-07-06 · **From:** RFC0025 / CR0178 WS1
>
> This protocol is committed **before** the first measured run so the result cannot be quietly
> reshaped. Git history is the freeze witness: the task set, metrics, N, and baseline below do
> not change between here and publication. Results are published regardless of outcome,
> including unflattering ones (the anti-hype editorial stance).

## Question

Does driving a task through sdlc-studio beat plain Claude Code with a good `CLAUDE.md` on the
same task, measured by tokens, wall time, defect escapes, and rework rate?

## Arms

- **A - sdlc-studio:** the full pipeline (spec -> plan -> implement -> verify -> reconcile).
  `tools/bench/arms/pipeline_CLAUDE.md`.
- **B - baseline:** plain Claude Code with a genuinely good `CLAUDE.md`
  (`tools/bench/arms/baseline_CLAUDE.md`) - **signed off 2026-07-08 by an independent review
  seat (not the harness author)** as genuinely good, no straw-man phrasing found (a straw-man
  baseline invalidates the comparison - CR0178 acceptance criterion).

## Task set (fixed)

Three small fixture repos, each with a **held-back acceptance suite the agent never sees**:

1. a greenfield feature addition,
2. a brownfield bug fix,
3. a second brownfield bug fix (different subsystem).

Fixtures and hidden suites are versioned in-repo under `tools/bench/fixtures/`.

## Metrics (per run)

| Metric | Definition |
| --- | --- |
| Tokens | Total tokens consumed, from the transcript |
| Wall time | End-to-end run duration |
| Defect escapes | The held-back suite fails after the arm declares "done" |
| Rework rate | Share of runs needing a follow-up fix pass |

## Sample size

**N = 5** runs per arm per task. A **de-risking spike runs N = 1 across the fixtures first** -
it proves the harness end-to-end and gives an early effect-size read before the full 5x cost
is committed. Report effect sizes with honest error bars at whatever N the budget allows; no
statistical-significance claims at small n.

## Controls

- Pin one model version per run and report it; cross-version comparison is out of scope.
- Publish the fixtures and this protocol with the results; invite replication.

## Publication

Repo-first under `docs/benchmarks/`. Published **regardless of direction of the result** - an
unflattering number with error bars beats a flattering assertion. Live-project anecdotes, if
any, are clearly labelled as anecdotal (not part of the measured N).

## Status

- [x] Protocol pre-registered (this file)
- [x] Harness + fixtures + hidden suites built (CR0178 WS2 / US0074)
- [x] N=1 spike run - see [2026-07-08-n1-spike.md](2026-07-08-n1-spike.md): 0 defect escapes
      either arm, no consistent directional win on tokens/wall-time. The spike's own finding
      is that these 3 fixtures don't yet exercise the pipeline's differentiating claims (all
      3 arm-A runs judged the tasks too small to warrant the pipeline) - **N=5 on this
      fixture set is paused pending a fixture-design decision**, not proceeding blind.
- [ ] N=5 measured run + published report (CR0178 WS3 / US0075)
