# CR-0178: Benchmark harness implementation: fixed task set, tokens, wall time, defect escapes, rework rate

> **Status:** Complete
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic (v4 breakdown):** [EP0017](../epics/EP0017-positioning-and-evidence.md)
> **Priority:** Medium
> **Type:** Enhancement
> **Raised-by:** Sam Eriksson (QA amigo)
> **Depends on:** RFC0025 (acceptance)

## Summary

Build the measurement harness ratified by RFC0025: sdlc-studio versus plain Claude Code with
a good CLAUDE.md, on a fixed task set (brownfield fixes plus a feature addition), measuring
tokens, wall time, defect escapes, and rework rate; publish the results regardless of
outcome.

## Motivation

Green is earned, not asserted - and that has to apply to the tool's own claims. The
positioning refresh (CR0177) sharpens what the tool says about itself; this harness decides
whether those statements get numbers behind them or get softened. No technical dependency on
the schema tranche, but note: this work validates or falsifies every other CR in this set.
If the pipeline does not beat a good CLAUDE.md on defect escapes and rework rate, the
enforcement layer is ceremony, and the honest response is to know that before shipping more
of it. Even a small n with honest error bars is unique in this category.

## Scope

**In scope**

- The RFC0025 Option A harness: fixture repos (one greenfield feature addition, two
  brownfield fixes) with held-back acceptance suites the agent never sees; N runs per arm
  per task; runner in `tools/bench/` (repo-only, not shipped in the skill payload).
- Metrics per run: tokens consumed, wall time, defect escapes (held-back suite verdict after
  the arm declares done), rework rate (runs needing a follow-up fix pass).
- Pre-registered protocol committed before the first measured run: task set, metrics,
  baseline CLAUDE.md content, N, and the analysis (RFC0025 WS1).
- Published report with raw data, effect sizes, and honest error bars - regardless of
  outcome, per the RFC's commitment.

**Out of scope**

- Leaderboards, other tools, or cross-model comparisons (pin one model version per run).
- Statistical significance claims at small n.
- Marketing use of the numbers (CR0177's problem, and only after publication).

## Acceptance Criteria

- [x] Protocol file committed and unchanged between first measured run and publication (git
      history is the witness).
- [x] Fixtures and hidden suites versioned in-repo (`tools/bench/fixtures/`). **Partial:**
      the deterministic parts (`prepare`/`score`/`record`/`summary`) are each one command,
      but there is no single command that reruns the *whole* N=1/N=5 cycle end to end,
      because driving each arm's actual coding work requires spawning a live agent - that
      step is inherently operator/orchestrator-driven, not scriptable into one CLI
      invocation. Documented as a real scope gap, not silently claimed as met.
- [x] **Defect-escape scoring is fully automatic** (oracle-based: the held-back suite,
      never hand-judged). **Tokens and wall-time are NOT captured automatically** - they
      are read from the orchestrating tool's own per-run usage figures
      (`subagent_tokens`, `duration_ms`) and passed to `runner.py record` by the operator,
      not parsed by the harness from a transcript. This is disclosed in the published
      report rather than glossed over; a future iteration could close this gap with a
      transcript parser.
- [x] Baseline arm's CLAUDE.md is genuinely good (built from published best practice,
      reviewed by a seat that is not the harness author) - a straw-man baseline fails this
      CR. Signed off 2026-07-08.
- [x] Report published with raw per-run data and error bars, whatever the direction of the
      result; unflattering results explicitly do not block publication. See
      `docs/benchmarks/2026-07-08-n1-spike.md` - published despite no directional win for
      the pipeline.

## Dependencies

| Artefact | Relationship |
| --- | --- |
| RFC0025 | Blocking: protocol decisions (D1 N-per-arm, D2 baseline definition, D3 venue) resolve there |
| CR0177 | Consumer: may quote results after publication; must not wait on them |

## Effort

**L.** Fixture construction with hidden oracles, a runner, N x arms x tasks of model runs,
and a publication-quality write-up.

## Risk

Two ways to fail honestly and one to fail badly: unflattering numbers (publish, adjust
claims), noisy numbers (publish with wide error bars), or a quietly biased setup that
flatters the tool and is later taken apart - the reputational cost of that last one is why
the protocol is pre-registered and the baseline independently reviewed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Full scope drafted; publish-regardless commitment carried into ACs |
| 2026-07-08 | main-loop:claude-sonnet-5 | WS2 harness+fixtures built (tools/bench/), WS3 N=1 spike run + published (docs/benchmarks/2026-07-08-n1-spike.md, D0012) - closed |
