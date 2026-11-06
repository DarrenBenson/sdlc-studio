# RFC-0062: Token-efficient delivery: a sprint costs at most 0.6M priced tokens per point, measured the same way in every supported harness

> **Status:** Draft
> **Decomposed-into:** CR0665, CR0666, CR0667, CR0668, CR0669
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

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
| 2026-11-06 | Claude Opus 5.5 | Open decisions resolved by the operator's rulings (D0411); phased plan added |
