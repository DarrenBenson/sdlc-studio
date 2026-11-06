# BG1271: `sprint cost --anatomy` counts a call from the second the run opened that the opening reading already holds, reads a zero, negative or quoted start budget as none, and leaves three boundaries and an AC2 pin loose

> **Status:** Open
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/cost_anatomy.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py, .claude/skills/sdlc-studio/scripts/tests/test_agent_definitions.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Evidence:** run eight (RUN-01M6RZQZ) BG1254 review round 1 and US1132 review round 1 ([new], non-blocking)
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T20:38:45Z

## Summary

From BG1254's review: (1) `started_at` is whole-second (`.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py:395`) while transcript timestamps carry milliseconds, so a call written just before `open_run`, in the same second, passes `moment > since` (`lib/cost_anatomy.py:147`) and is counted although the opening meter reading already holds it, which makes 'the whole equals the meter's delta over the run' (`reference-sprint.md:639`) false at that boundary (LC-018); (2) the tool-output window's boundary is unpinned: `moment <= since` to `moment < since` (`cost_anatomy.py:233`) survives `test_cost_anatomy.py`; (3) the unparsable-start fallback is unpinned: `else None` to `else whole` on `cut = _after(whole, since)` (`cost_anatomy.py:317`) survives and reads the whole session under a window that names the run's start. From US1132's review round 1, non-blocking: (4) the start-budget boundary is unpinned: `contexts[0] >= budget` survives, no fixture agent starting exactly at the budget (`cost_anatomy.py:333`, `tests/test_cost_anatomy.py:324-366`); (5) a `cost.agent_start_budget` of 0, a negative number or a quoted number reads silently as no budget and renders 'no budget is configured', while `reference-config.md:332` documents only `off` as flagging none (`cost_anatomy.py:289-294`); (6) AC2's pin reads only `reference-epic.md`'s example block and a `single|one message` phrase, so replacing 'Launch the first agent alone and the rest once it has started' with 'Launch every agent of the wave together.' survives (`reference-epic.md:749`, `tests/test_agent_definitions.py:183-199`). Line numbers are at review round 1, before `3e8c5c77`.

## Steps to Reproduce

(1) Open a run at `12:00:00.700` (recorded `started_at` `12:00:00`) over a transcript holding a call stamped `12:00:00.400`: the anatomy counts it, and its total exceeds the meter's delta over the run. (2) to (4) Apply each mutant and run `test_cost_anatomy.py`: green. (5) Set `cost.agent_start_budget: 0` and run `sprint cost --anatomy`: 'no budget is configured'. (6) Make the prose replacement at `reference-epic.md:749` and run `test_agent_definitions.py`: green.

## Proposed Fix

Record `started_at` with the precision the transcripts carry, or attribute a call in the run's opening second to the opening reading, and say which in `reference-sprint.md`; add a fixture per boundary (a tool output stamped exactly at the start, an unparsable start, an agent starting exactly at the budget); refuse or warn on a start budget that is neither a positive integer nor `off`, and document it in `reference-config.md`; pin AC2 on the epic prose's first-agent-alone sentence, not only its example block.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: From BG1254's review: (1) `started_at` is whole-second (`.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py:395`) while transcript timestamps carry...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: (1) Open a run at `12:00:00.700` (recorded `started_at` `12:00:00`) over a transcript holding a call stamped `12:00:00.400`: the anatomy counts it, and its...
- [ ] **AC3** The proposed fix lands, pinned by a test: Record `started_at` with the precision the transcripts carry, or attribute a call in the run's opening second to the opening reading, and say which in...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
