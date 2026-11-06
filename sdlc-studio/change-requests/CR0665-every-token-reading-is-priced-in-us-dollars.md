# CR-0665: Every token reading is priced in US dollars from a dated per-model price table, beside the input-equivalent figure

> **Status:** Complete
> **Decomposed-into:** EP0299
> **Parent:** RFC0062
> **Priority:** High
> **Type:** Feature
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Evidence:** RFC0062 Phase 1; run six's transcripts and the 2026-11-06 capture of one headless session per CLI harness.
> **Date:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T11:17:47Z

## Summary

The priced figure is input + 5 x output + 1.25 or 2 x cache write + 0.1 x cache read, the same for every model (`run_state.TOKEN_WEIGHTS).` It cannot show the saving from moving a reviewer to a cheaper model, and it cannot compare a Codex or Copilot run with a Claude one, whose providers price tokens differently. RFC0062's bar and its model-routing trial both need a money figure.

## Impact

Every sprint report, velocity row and lane row. Without it a cheaper model shows no saving and no two harnesses can be compared.

## Acceptance Criteria

- [ ] A price table shipped with the skill gives, per model, its input, output, cache-read and cache-write (5-minute and 1-hour) prices per million tokens, the date they took effect and their source; a project can override or extend it in config
- [ ] The sprint report, each unit row and the velocity row state an estimated cost in US dollars beside the priced tokens, computed from each reading's own model and components
- [ ] A reading whose model has no price is reported as not priced and names the model, never as zero, and the run total says what share of the spend it covers
- [ ] A Copilot CLI reading reports its premium requests as their own unit beside its tokens
- [ ] The report states the price table's effective date and names it as stale once it is older than a configured age

## Recommendation

A small lib/prices.py over a dated table in templates; readings already carry model and components, so the dollar figure is a pure function of them.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Raised |
