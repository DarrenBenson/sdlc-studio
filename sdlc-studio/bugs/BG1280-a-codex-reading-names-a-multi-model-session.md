# BG1280: A Codex reading names a multi-model session `A, B` with no per-model split, so a run that brings in a new model books the workspace's whole pre-run history as run spend in its dollar cost

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_codex.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_codex.py, .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, changelog.d/BG1280.md
> **Evidence:** the between-releases review before v6.3.0 (D0427, LL0005), code leg A; repro under scratchpad rel63/legs/scratch-a/
> **Created:** 2026-11-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-08T13:06:30Z

## Summary

The Codex reader names a multi-model reading 'A, B' rather than `run_state.SESSION_MODEL_MIXED`, and gives no per-model split. `_split_fields` therefore books the whole cumulative workspace total under a pseudo-model named for the current model set. When that set changes between the open and close stamps (a new model used in the run, or a lane on another model), `_split_delta` treats each name absent from a reading as 0. The opening reading's entire pre-run history is booked as a delta under the old model, and the closing total in full under the joined name. The Dollar cost and Dollars per point rows (`run_state.usd)` then price spend the run never made.

## Steps to Reproduce

python3 rel63/legs/scratch-a/`codex_mix.py` <tmp> <scripts> (history thread gpt-5.3-codex 1,010,000 tokens; run adds a gpt-6.1-sol thread of 51,000) -> 'open model: gpt-5.3-codex' / 'close model: gpt-5.3-codex, gpt-6.1-sol' / 'run tokens delta: 51000' / `by_model` delta {'gpt-5.3-codex': input 1000000 output 10000, 'gpt-5.3-codex, gpt-6.1-sol': input 1050000 output 11000} / 'usd: 1.89 covered: 0.487 ... unpriced: [gpt-5.3-codex, gpt-6.1-sol]'. That is $1.89 for a model that spent nothing in the run, and a split summing to 2,071,000 against a 51,000 delta.

## Proposed Fix

Have `meter_codex` return a real `BY_MODEL` split (sum each thread's components under its own threads.model) and `SESSION_MODEL_MIXED` for >1 model. In `run_state`, mark a split that `_split_fields` synthesised from a single model name; have `_split_delta` fall back to whole-span booking when such a synthesised name differs across a span's readings, or when the per-model sums do not equal the span delta.

## Acceptance Criteria

- [ ] **AC1** Given a Codex store with threads on two models, when `meter_codex.read` reads it, then the reading's model is `run_state.SESSION_MODEL_MIXED` and it carries a per-model split that sums each thread's components under its own `threads.model`, the split summing to the reading's total. Fails on: the model named `', '.join(sorted(models))` with no split.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_codex.py::CodexMeterTests::test_a_two_model_reading_is_split_per_model
- [ ] **AC2** Given a run whose opening reading holds 1,010,000 tokens of history on gpt-5.3-codex and whose closing reading adds a 51,000-token thread on gpt-6.1-sol, when the report prices the run, then the dollar delta prices only gpt-6.1-sol's 51,000 tokens and books nothing under gpt-5.3-codex. Fails on: the observed $1.89 for a model that spent nothing in the run.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_a_model_new_to_the_run_books_only_its_own_spend
- [ ] **AC3** Given two readings of any harness whose split `_split_fields` synthesised from a single model name, and whose names differ between the span's open and close, when `_split_delta` derives the span, then it books the span whole, or reports it unpriced, never the opening reading's history as a delta. Fails on: a name absent from one reading treated as 0.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_a_synthesised_split_whose_name_changes_is_not_booked_as_history

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Filed |
| 2026-11-08 | Claude Opus 5.5 (grooming) | The changelog fragment joins Affects (D0428) |
