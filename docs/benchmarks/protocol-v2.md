# Benchmark protocol v2 (pre-registered)

> **Status:** pre-registered · **Date:** 2026-07-08 · **Supersedes:** [protocol.md](protocol.md) (v1)
> · **Trigger:** the [N=1 spike](2026-07-08-n1-spike.md) + decision D0012.
>
> v1's fixture set could not exercise the pipeline's differentiating claims: all three arm-A
> spike runs correctly judged the small single-file tickets too small to warrant the pipeline
> and behaved like plain Claude Code. This file is a **new pre-registration made openly** - v1's
> frozen body is untouched (its freeze discipline is honoured, not bypassed), and git history
> remains the witness: the task set, metrics, N, arms and analysis below do not change between
> here and publication. Results are published **regardless of outcome**, including unflattering
> ones.

## Questions

1. **Primary (unchanged from v1):** does driving a task through sdlc-studio beat plain Claude
   Code with a good `CLAUDE.md` on the same task?
2. **Secondary (now explicit):** on tasks below the pipeline's engagement threshold, does the
   pipeline correctly avoid overhead and match the baseline? (Parity on Tier 2 is a *positive*
   scale-to-size finding; ceremony spent on tiny tickets would be a defect.)
3. **Cost (new):** with model-tier routing enabled, does the pipeline deliver equal quality at
   a lower cost index?

## Arms

- **A - sdlc-studio:** the pipeline (`tools/bench/arms/pipeline_CLAUDE.md`). The judgement
  wording ("scale to the size of the ticket") is deliberately retained from v1 - forcing
  pipeline invocation would rig the comparison and invalidate Tier 2.
- **B - baseline:** plain Claude Code + the independently signed-off good `CLAUDE.md`
  (`arms/baseline_CLAUDE.md`, sign-off 2026-07-08).
- **R - routed pipeline:** arm A plus `routing.enabled: true` and the published model map
  (`arms/routed_config.yaml`); delivery workers spawn on the recommended tier; the run
  records its model mix.

**Environmental isolation (hardened since v1):** workspaces are prepared OUTSIDE this repo;
arms A/R get the skill copied INTO the workspace (`.claude/skills/sdlc-studio`); arm B's
workspace simply does not contain the skill - absence, not instruction.

## Task set (fixed)

- **Tier 1 (differentiating):** `multifile-notify-digest` (hidden-requirement discovery:
  under-specified ticket, multi-file service, a spec whose existing requirements silently
  interact with the ticket) and `change-request-ledger-drift` (drift control: a CR whose
  tempting implementation breaks adjacent spec'd behaviours; includes a deterministic
  spec-updated check). Each fixture's hidden suite is validated both ways before freeze
  (fails on the naive/seeded variant, passes on the reference solution); the fairness
  invariant holds - everything needed to pass is present in the visible workspace.
- **Tier 2 (scale-down control, unchanged from v1):** `greenfield-csv-dedupe`,
  `brownfield-pagination`, `brownfield-lru-cache`.

Fixtures, hidden suites and audit quizzes are versioned in-repo under `tools/bench/fixtures/`;
their content at freeze is fixed by the git commit that lands this file.

## Metrics (per run)

| Metric | Definition |
| --- | --- |
| Tokens | Total tokens consumed - parsed from the orchestrator's per-run usage output via `transcript_metrics.py` (`metrics_source: parsed`); hand-entered values are stamped `manual` and disclosed |
| Wall time | End-to-end run duration, same source |
| Defect escapes | The held-back suite fails after the arm declares "done" (oracle-scored, never judged) |
| Rework rate | Share of runs needing a follow-up fix pass after a verified-done claim; a deliberate mutation-check (re-running a new test against the pre-fix code) is verification practice, NOT rework (v1 spike definition carried forward) |
| **Auditability (new)** | Held-back audit quiz scored by `audit_quiz.py`: outcome answerability from the finished workspace only, never artifact presence. Class D (cited runnable evidence must pass the workspace and fail a seeded mutant) + class T (citation-validated trace/decision answers). Reviewer-independence is reported descriptively at **weight 0** - a single-agent arm structurally cannot score it, so any weight would be a by-construction point for the pipeline arms |

## Sample size

- **Tier 1: N = 5** per arm per fixture. **Tier 2: N = 2** per arm per fixture (the control
  claim needs directional confirmation, not tight error bars).
- **Spike/calibration first: N = 1** per arm across Tier 1 (arms A/B/R), published and
  labelled, never pooled with measured runs. The calibration may adjust fixture
  **size/engagement only** (does arm A actually engage the pipeline?); hidden suites and
  quizzes are frozen by this file and do not change after it.
- v1 spike data is reported alongside as the Tier-2 n=1 datapoint, labelled, never pooled.

## Analysis

Per-tier reporting; no cross-tier pooling; means with min/max (honest error bars at small n;
no statistical-significance claims). Cost index for arm R = units x operator-supplied
relative tier prices (`runner.py summary --price ...`); the price map is published with the
results. Auditor-agent variance is acknowledged, not laundered (one auditor pass per run,
pinned model, token-capped).

## Pre-declared cut order (a budget cut is not cherry-picking if declared now)

1. Tier 2 drops to zero new runs - the v1 spike rows stand as the labelled control datapoint.
2. Tier 1 N=5 -> N=3.
3. Drop `change-request-ledger-drift`; keep `multifile-notify-digest` (hidden-requirement
   discovery is the single strongest claim).

Never cut: the calibration spike (the insurance against repeating v1's engagement failure at
5x cost) or the audit quizzes (the new dimension is the point of v2).

## Status

- [ ] Harness hardened + fixtures + quizzes built and validated (CR0193 / US0086-US0088)
- [ ] N=1 calibration re-spike (arms A/B/R x Tier 1) run + published (US0089)
- [ ] Fixture-engagement verdict: proceed to N=5 / adjust fixtures / stop
- [ ] Measured runs (Tier 1 N=5, Tier 2 N=2) + published report
