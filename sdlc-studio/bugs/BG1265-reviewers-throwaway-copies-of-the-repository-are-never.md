# BG1265: Reviewers' throwaway copies of the repository are never removed and carry no history, so they fill the temp quota and fail history-dependent tests each reviewer must then triage

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/templates/agents/sdlc-reviewer.md, .claude/agents/sdlc-reviewer.md, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_agent_definitions.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** the orchestrator's friction log (R8-F11), with run eight (RUN-01M6RZQZ) US1129 review rounds 1 and 2 and BG1258 review round 1 ([pre-existing])
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T20:38:05Z

## Summary

Reviewers mutate and run suites in throwaway archive copies of the tree (200 MB to 2 GB each) under the session scratchpad, and nothing removes them: after about 25 reviews in run eight they filled the temp volume's 5 GB quota and a command failed with `EDQUOT`. Neither `.claude/skills/sdlc-studio/templates/agents/sdlc-reviewer.md` nor the `critic.py brief` text says where to run a mutant or to delete the copy (neither carries a copy, worktree or clean-up instruction). The copies are also history-less, so each reviewer meets the same environmental failures and spends a pass proving them pre-existing: `test_lean_release_notes_v62.py` (4), `test_persona_coherence.py` (2), `test_lean_prd_refresh.py` (1) and `test_gate.py` `SurfaceCompletenessTests` (no tracked files without git) fail in a copy at the base and at the head alike (US1129 rounds 1 and 2). A raw 8-worker run also ignores the `serial_only` mark, so `test_status.py` `GatherPerformanceTests` misses its 3.0 s headline bound (US1129 round 2, BG1258 round 1).

## Steps to Reproduce

Run a wave of reviews with mutation passes and `du -sh` the session scratchpad after each: it grows by a tree per review and never shrinks. In one archive copy run the skill suite with 8 workers: the tests above fail there and pass in a checkout with history run the way the gate runs it.

## Proposed Fix

Tell the reviewer, in the shipped `sdlc-reviewer` definition and in the brief's mutation-pass text, to mutate in a detached `git worktree add` under the scratchpad (it shares the object store and keeps history) rather than an archive copy, to run suites the way the project's gate runs them (here `tools/run-suite.sh`), honouring its marks, and to remove the worktree with `git worktree remove --force` before it hands back; have `critic.py record` name any detached worktree under the scratchpad still registered. Pin the definition's wording in `test_agent_definitions.py`.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Reviewers mutate and run suites in throwaway archive copies of the tree (200 MB to 2 GB each) under the session scratchpad, and nothing removes them: after...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Run a wave of reviews with mutation passes and `du -sh` the session scratchpad after each: it grows by a tree per review and never shrinks.
- [ ] **AC3** The proposed fix lands, pinned by a test: Tell the reviewer, in the shipped `sdlc-reviewer` definition and in the brief's mutation-pass text, to mutate in a detached `git worktree add` under the...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
