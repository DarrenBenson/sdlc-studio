# CR-0669: The benchmark runs a fixture headless in any supported CLI against a pinned skill version and records the usage that CLI prints

> **Status:** Complete
> **Decomposed-into:** EP0299
> **Parent:** RFC0062
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** tools/bench/runner.py
> **Evidence:** RFC0062 Phase 1; run six's transcripts and the 2026-11-06 capture of one headless session per CLI harness.
> **Date:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T11:17:51Z

## Summary

tools/bench (RFC0025, CR0178) prepares a fixture workspace and scores it, but an agent session has to be run by hand and its tokens are entered by hand (`metrics_source` manual). RFC0062 needs a baseline per harness against the skill pinned at 5057f7ef, and a re-run after the savings land, measured the same way.

## Impact

Without it the consuming-project cost, which decides adoption, cannot be measured in any harness except by hand.

## Acceptance Criteria

- [ ] runner.py prepare --harness <h> --skill-ref <commit> installs that commit's skill into the harness's skill directory in the workspace
- [ ] runner.py run executes the arm's prompt headless in that CLI, records tokens from the CLI's printed usage through the same normaliser lanes use, the wall time and the held-back suite score, and marks the metrics measured
- [ ] runner.py summary reports each fixture, arm and harness, with the estimated US dollar cost where the model is priced

## Recommendation

Reuse the lane normalisers so the benchmark and the sprint report count tokens one way.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Raised |
