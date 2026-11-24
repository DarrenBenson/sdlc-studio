# BG1513: lane return --agent cannot price a builder spawned from another project's session: it looks for the transcript only under the lane repository's own projects directory

> **Status:** Fixed
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/lib/verdict_provenance.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_priced.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_provenance.py, changelog.d/BG1513.md
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T17:52:19Z

## Summary

The website run's builders were spawned from the skill repository's session, so their transcripts live under that project's ~/.claude/projects directory. `sprint.py --root <web> lane return --agent <id>` warned 'no session transcript (*.jsonl) in the website project's directory' and left the lane unpriced. The same lookup leaves `critic.py record` printing 'verdict file provenance is unknown' for every website verdict in that run, because the reviewer's transcript sits under the skill repository's project directory.

Reproduced at cecc9dfe7 (2026-11-24): `run_state.agent_transcript_tokens` looks only in `SDLC_STUDIO_TRANSCRIPTS` or `_harness_transcript_dir(repo_root)`. With a fixture HOME holding project A's session and its `subagents/agent-b7.jsonl`, the call from A prices the agent (110) and the same call from repository B returns `priced: None` with `no session transcript (*.jsonl) in <B's directory>`.

The `critic.py record` half, reproduced the same day in a throwaway HOME: `verdict_provenance._contexts` reads the session named by `CLAUDE_CODE_SESSION_ID` only from `SDLC_STUDIO_TRANSCRIPTS` or `_harness_transcript_dir(repo_root)`. With that session's main thread and reviewer `r1`'s transcript (holding its Write of the verdict file) under project A's folder, `verdict_provenance.read` for a verdict file in repository B returns `provenance:unknown` with `session <id> has no transcript in <B's folder>`. With the same session under B's own folder it returns `session:<id> agent:r1`.

Both halves are one defect: each reader looks for a session's transcripts only under the lane repository's own folder in the store. BG1596 is a different cause and stays apart: there the session is found, and provenance reads `unknown` because a repair builder whose prompt names the verdict path is taken as the briefed agent.

## Steps to Reproduce

1. From project A's session, spawn a builder for a lane in repository B.
2. Run sprint.py --root B lane return --agent <id>: it warns that no transcript exists under B's projects directory and leaves the lane unpriced.
3. From the same session, brief a reviewer for a unit in repository B, have it write the verdict file, and run `critic.py record --from-verdict <path> --root B`: the row records `provenance:unknown` and says the session has no transcript in B's folder.

## Proposed Fix

Give `run_state` one finder for a session's folder across the harness's projects store (`~/.claude/projects`), the lane repository's own folder first, and use it in both readers. In `run_state.agent_transcript_tokens`, when the lane repository's own directory holds no `agent-<id>.jsonl`, search the session subagents directories of every other project for it. Name the directory read on the priced line `lane return` prints, and name every directory searched when none holds it. In `verdict_provenance._contexts`, when the repository's own folder holds no `<session>.jsonl`, read the session from the other project's folder that holds it, and name that folder in the note `critic.py record` prints. `SDLC_STUDIO_TRANSCRIPTS`, when set, still names the only folder read.

## Acceptance Criteria

- [ ] **AC1** Given a builder whose transcript lies under another project's directory in the harness's projects store, and none under the lane repository's own, when `sprint.py lane return --agent` names it, then the lane is priced from that transcript and the output names the directory it was read from. Fails on: a cross-repository lane left unpriced with a warning that no transcript exists.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_priced.py::LanePricedTests::test_an_agent_spawned_from_another_project_s_session_is_priced
  - **Verified:** yes (2026-11-24)
- [ ] **AC2** Given a transcript for the agent under the lane repository's own project directory and another of the same name under a second project, when `lane return --agent` runs, then the lane repository's own is the one read. Fails on: the wider search preferring a foreign transcript over the local one.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_priced.py::LanePricedTests::test_the_lane_repository_s_own_transcript_wins_over_another_project_s
  - **Verified:** yes (2026-11-24)
- [ ] **AC3** Given an agent id with no transcript under any project directory, and a second project directory in the store beside the lane repository's own, when `lane return --agent` runs, then it warns naming the agent, the lane repository's directory and the other project's directory it searched, and records no priced cost. Fails on: a warning that names only the lane repository's directory (today's), or a missing agent priced as nought.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_priced.py::LanePricedTests::test_an_unknown_agent_names_every_directory_searched
  - **Verified:** yes (2026-11-24)
- [ ] **AC4** Given a throwaway HOME whose session store holds the session's main thread and reviewer `r1`'s transcript, with its Write of the verdict file, under project A's folder only, and a verdict file a brief issued for a unit in repository B, when `critic.py record --from-verdict <path> --root B` runs with `CLAUDE_CODE_SESSION_ID` naming that session and `SDLC_STUDIO_TRANSCRIPTS` unset, then the row's Source cell carries `session:<id> agent:r1` and the printed note names agent r1 and A's folder. Fails on: `provenance:unknown` with `session <id> has no transcript in <B's folder>`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_provenance.py::VerdictProvenanceTests::test_a_reviewer_in_another_project_s_session_is_named
  - **Verified:** yes (2026-11-24)
- [ ] **AC5** Given the same session under repository B's own folder, and a decoy transcript of the same session id under project A's folder in which another agent wrote the file, when `critic.py record` runs for B, then the Source cell carries `session:<id> agent:r1` read from B's folder, as today, and the decoy is not read. Fails on: the wider search reading another project's session ahead of the repository's own.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_provenance.py::VerdictProvenanceTests::test_a_same_project_reviewer_resolves_from_its_own_folder
  - **Verified:** yes (2026-11-24)

## Impact

A cross-repository run reports no cost for its lanes, so its cost per point is understated, and every verdict it records reads `provenance:unknown`, so the record cannot name the reviewer that wrote it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: reproduced at cecc9dfe7; scoped to the lane return, the critic provenance half reported apart; AC3 names a new test, as the existing one passes today; Points 1 to 2 |
| 2026-11-24 | Sam Eriksson (qa) | Folded the `critic.py record` provenance half back in under D0561: reproduced in a throwaway HOME; AC4 (cross-project reviewer named) and AC5 (same-project control); BG1596 kept distinct; Affects adds lib/verdict_provenance.py and test_critic_verdict_provenance.py; Points 2 to 3 |
