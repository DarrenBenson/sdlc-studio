# BG1293: A Codex lane that times out or prints no usage leaves no delegated record, and since BG1288 its worktree thread is left out of the reading, so its spend reaches a Codex-metered run zero times

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_codex.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_codex.py
> **Evidence:** BG1288 round-2 review (qa-seat-BG1288-r1), probe S7
> **Created:** 2026-11-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-08T14:21:39Z

## Summary

From BG1288's round-2 review (qa-seat-BG1288-r1, round 2, non-blocking [regression]): VERDICT: APPROVE
leaving every lane-worktree thread out of the reading drops an unmetered Codex lane's spend from a Codex-metered run (`meter_codex.py`:151, docstring `meter_codex.py`:26-29, changelog.d/BG1288.md:6-8): by execution in isolated exports of 4c236fe4^, 4c236fe4 and e51dad92 (probe /tmp/claude-1000/-home-darren-code-DarrenBenson-sdlc-studio/acd73b30-154a-4170-83eb-043073708d4b/scratchpad/rel63/qa/BG1288-r2/tools/probe7.py case S7, temp HOME and `CODEX_HOME)`, a Codex lane thread that spends 44,000 with no delegated record, which is what `sprint lane run` leaves when the CLI times out, exits non-zero or prints no usage (lanes.py:616-617), reads 11,000 at the repair for a true 55,000 (55,000 at both 4c236fe4^ and 4c236fe4). The docstring's "a lane's spend reaches the run once, through its delegated record" and the changelog's "a lane is counted once, through its delegated record" are false for that lane, which reaches the run zero times [LC-018]. The lane run warns that an unmetered lane records no priced cost (lanes.py:690), and the design is the one BG1288 round 1 prescribed.

## Steps to Reproduce

Probe S7 of rel63/qa/BG1288-r2/tools/probe7.py: a workspace-root Codex thread growing 11,000 and a lane-worktree thread spending 44,000 with no delegated record; the run's actual reads 11,000 at e51dad92, 55,000 at 4c236fe4.

## Proposed Fix

When a lane-worktree thread spent in the run and no delegated record names its lane, count that thread in the reading (and say so in the basis), so an unmetered lane is counted once from the store; correct the docstring at `meter_codex.py`:26-29 and BG1288's changelog wording.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: From BG1288's round-2 review (qa-seat-BG1288-r1, round 2, non-blocking [regression]): VERDICT: APPROVE leaving every lane-worktree thread out of the reading...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Probe S7 of rel63/qa/BG1288-r2/tools/probe7.py: a workspace-root Codex thread growing 11,000 and a lane-worktree thread spending 44,000 with no delegated...
- [ ] **AC3** The proposed fix lands, pinned by a test: When a lane-worktree thread spent in the run and no delegated record names its lane, count that thread in the reading (and say so in the basis), so an...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Filed |
