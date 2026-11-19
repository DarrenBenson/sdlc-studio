# CR-0746: The session meter finds a Claude Code session's transcript store from the session id the harness exports, so a run driven from another repository is priced without SDLC_STUDIO_TRANSCRIPTS

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Feature
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, changelog.d/CR0746.md
> **Evidence:** run eighteen, lane L4 builder, 2026-11-19: BG1605's AC2 passes on the unchanged tree once the variable is set; the website run RUN-01M7R7KN's archive holds no stamp because it was never set
> **Date:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T12:38:23Z

## Summary

The meter resolves the transcript store from the repository path, so a run planned and closed in a second repository from a session started in the first takes no token stamp unless the operator sets `SDLC_STUDIO_TRANSCRIPTS.` The website run of 2026-11-19 closed NOT MEASURED for that reason. Claude Code exports `CLAUDE_CODE_SESSION_ID` to every command it runs, and the session's transcript is the one file named for that id under the projects store, so the meter could find it with no variable. The plan's new warning names the remedy, but the operator still has to act on it.

## Impact

A run driven from another repository is priced by default, so O11's cost per point covers every run, not only those whose operator set a variable.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Proposed Fix

When no store is named and the repository's own store holds no transcript, look for `<CLAUDE_CODE_SESSION_ID>.jsonl` under the Claude projects store and stamp from it, saying which file it read. Keep `SDLC_STUDIO_TRANSCRIPTS` as the override.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Raised |
