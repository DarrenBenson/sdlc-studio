# RFC-0062: Token-efficient delivery: a sprint costs at most 0.6M priced tokens per point, measured the same way in every supported harness

> **Status:** Draft
> **Decomposed-into:** CR0665, CR0666, CR0667, CR0668, CR0669, CR0670, CR0671, CR0672, CR0673, CR0674, CR0675, CR0676, CR0677, CR0678, CR0679, CR0680, CR0681, CR0682, CR0683
> **Size:** XL
> **Evidence:** Run six (RUN-01M6NH7W) transcripts, recounted 2026-11-06 at 37.5M priced against RPT0025's 36.8M; a capture of one headless session in each of Claude Code, Cursor CLI, Codex CLI, Copilot CLI and OpenCode on 2026-11-06.
> **Date:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T11:15:48Z

## Summary

If the skill costs too many tokens, people will not use it. Run six cost 1.27M priced tokens per point, and the operator's norm is 1M. This RFC sets a bar before anything is measured (LL0036), measures every supported harness the same way, reviews where the tokens go, and delivers the savings with budget gates so they cannot quietly return (LL0027).

Where run six's tokens went, recounted from the transcripts: the orchestrating session 15.1M (40%; 323 calls at an average context of 407k), builders 12.5M (34%; 14 agents, 53 calls each, average context 104k), reviewers 7.9M (21%; 18 reviews, about 0.44M each, the cost of building a 1-point unit), repairs 1.9M (5%; 8 of 13 units went to a second review round). Cache reads were 70% of the spend, cache writes 17% and output 13%, most of it reasoning. Every subagent starts at about 40k tokens of context before it reads a file, and re-reading that base cost about 5.7M (15%).

Two measurement gaps block the review. The priced figure weights cache and output but not the model's price, so a cheaper model shows no saving. And only the Claude Code and Cursor readers exist: Copilot CLI (US0987) and OpenCode (US0988) are Draft, and Codex CLI is not recognised. A capture on 2026-11-06 shows that every one of these CLIs prints its usage in headless JSON, but they disagree on what input means: Codex and Copilot count cached tokens inside input, while Claude Code and OpenCode count them apart. A headless session's starting context was 28.5k tokens in Claude Code, 27.6k in Copilot CLI, 15.1k in Cursor CLI, 14.5k in Codex CLI and 11.7k in OpenCode.

## Design Options

- **A - Optimise this repository's own sprints only, measured with the Claude meter. Cheapest, but it misses the consuming-project cost that decides adoption, and every other harness.**
- **B - Measure first, then review and optimise across harnesses. Phase 1 measures every installed CLI the same way, adds a dated per-model price table and a per-role cost breakdown. Phase 2 baselines the benchmark against the skill pinned at 5057f7ef. Phase 3 reviews seven areas: orchestration, agent starting context and briefs, review cost, first-time-right, tool output, ceremony, and models and effort. Phase 4 delivers the savings with budget gates. Phase 5 re-measures against the bar.**
- **C - Cut ceremony by decree now, without measurement. Fast, but it acts on impressions (LL0030), cannot show a negative result (LL0036), and risks quality nobody measured.**

## Recommendation

Option B. The bar, ruled by the operator on 2026-11-06 (D0411): this repository's sprints cost at most 0.6M priced tokens per point with at most 20% of units needing a second review round and no rise in defects found later; the benchmark's skill arm costs at least 40% less per fixture than the skill at 5057f7ef, at an equal or better held-back pass rate, in each CLI harness measured; every CLI reader agrees with the harness's own reported usage within 5%, and a harness with no readable usage says so and why; every report states an estimated cost in US dollars from a dated price table beside the token figures.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Choose between options A, B and C | Resolved: Option B, under the operator's rulings recorded as D0411 |
| D2 | Which harnesses, and what spend | Resolved (D0411): Claude Code, Cursor CLI, Copilot CLI, Codex CLI and OpenCode, on existing subscriptions or free models only; Gemini CLI waits until it is set up |
| D3 | What the review may do with a check that does not earn its place | Resolved (D0411): retire or tier it, each by its own recorded decision listed at the sign |

## Phased Plan

1. **Measure (one run).** Price every reading in US dollars from a dated per-model price table; break a run's spend down by role; run a lane headless in any supported CLI and price it from the usage that CLI prints, normalised to one basis; finish the Copilot CLI and OpenCode store readers and add Codex CLI's; validate each reader against the harness's own total; let the benchmark run a fixture headless in any supported CLI.
2. **Baseline.** Run the benchmark's fixtures against the skill pinned at 5057f7ef: Claude Code three times per fixture and arm, each other CLI once or twice; take a static inventory of the tokens each command loads, each brief's size and each script's common-path output.
3. **Review.** One independent reviewer per area, working from the Phase 1 and 2 data: orchestration, agent starting context and briefs, review cost, first-time-right, tool output and exploration, ceremony (LL0056), and models and effort. Each finding is filed with its estimated saving and its risk to quality.
4. **Deliver.** Findings refined into units ranked by saving per point. Each unit carries a before-and-after measurement criterion and, where it can, a budget gate.
5. **Re-measure.** The same benchmark and one sprint of this repository, judged against the bar; publish cost per point by harness.

## Phase 3 Result (2026-11-06)

Six independent reviewers (orchestration, agent starting context and briefs, review cost, first-time-right,
tool output, ceremony) worked from run six's transcripts; one consolidating agent merged their 45 findings
into 14 CRs and counted each saving once. Savings are priced tokens per run of run six's shape (37.5M, 29 points).

| CR | Change | Saving |
| --- | --- | --- |
| CR0670 | Each wave and the close in a fresh orchestrator session from an on-disk resume brief | 8.54M |
| CR0671 | A commit-time sweep lane and a static census-marker check | 1.95M |
| CR0672 | A deterministic `sprint.py drive` loop and a multi-worktree `lane land` | 1.73M |
| CR0673 | One shipped mutation runner for author and reviewer, recorded by the self-check | 1.72M |
| CR0674 | Restricted-tool agent definitions and a three-line hand-back | 1.63M |
| CR0675 | A hostile-runtime fixture kit for the verifier core | 0.94M |
| CR0676 | Changelog fragments generated from the unit | 0.89M |
| CR0677 | Size budgets for AGENTS.md, the consuming template and SKILL.md | 0.85M |
| CR0678 | `repo_map.py outline` and symbol ranges in both briefs | 0.77M |
| CR0679 | The critic brief as a complete review packet, with a repair-scoped rejoinder | 0.61M |
| CR0680 | Small same-wave units batched into one reviewer; a fresh round-2 reviewer recorded as such | 0.38M |
| CR0681 | Self-writing trailers and one-line success output on the commit path | 0.25M |
| CR0682 | Executed per-criterion claims, docs naming what changed, captures, defect-class tags | about 0 tokens; the second-round bar |
| CR0683 | Three run-seven steps that leave state the next step refuses | not grounded |

De-duplicated total: about 20.0M per run (53%), projecting 0.60M priced per point against run six's 1.29M; the
conservative case is 0.72M. Orchestration alone (CR0670, CR0672) gives 0.94M, so the bar needs the rest too.
CR0671, CR0673, CR0675 and CR0682 together take run six's second-round count from 8 of 13 units to about none.
Not covered: models and effort, which waits for the Phase 2 benchmark's routed arm and for dollar pricing.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
| 2026-11-06 | Claude Opus 5.5 | Open decisions resolved by the operator's rulings (D0411); phased plan added |
| 2026-11-06 | Claude Opus 5.5 | Phase 3 result recorded: CR0670-CR0683 filed from six lens reviews, about 20.0M per run de-duplicated |
