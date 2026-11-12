# US1014: A recorded verdict names the agent that was briefed and wrote it, read from the harness transcript

> **Status:** Ready
> **Delivers:** CR0619
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/lib/verdict_provenance.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_provenance.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/reference-review.md, changelog.d/US1014.md
> **Epic:** EP0280
> **Points:** 5
> **Depends on:** US1012
> **Persona:** Jonah Reyes

## User Story

**As** a team lead whose developers each run review agents
**I want** each recorded verdict to name the agent that received the brief and wrote the file, read from the harness's own session store, with a warning when the file was last written by another context
**So that** an orchestrator's edit between the reviewer and the record can be seen instead of being taken on trust

## Acceptance Criteria

- **AC1:** Given fixture Claude Code transcripts in which subagent `r1` received the issued verdict path and wrote that file with its Write tool, when `critic.py record --from-verdict <path>` runs with `SDLC_STUDIO_HARNESS=claude` and that session id, then the row's `Source` cell carries `session:<id> agent:r1` after the hash, and `show` labels the verdict as written by agent r1.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_provenance.py::VerdictProvenanceTests::test_the_briefed_agent_that_wrote_the_file_is_named_on_the_row
- **AC2:** Given that the file's bytes differ from the content `r1`'s write carried, or that a later write to the path sits in another context's transcript (the main thread's), when `record` runs, then it writes the row and warns, naming the briefed agent and the context that last wrote the file.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_provenance.py::VerdictProvenanceTests::test_a_file_rewritten_by_another_context_warns
- **AC3:** Given a harness whose store is not read (`SDLC_STUDIO_HARNESS=cursor`), or Claude transcripts holding no write of the path, when `record` runs, then the row's provenance reads `unknown`, `record` says why, and the row never names an agent.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_provenance.py::VerdictProvenanceTests::test_an_unread_store_records_unknown_provenance

## Notes

- Release: after 6.3.0, in run ten (D0461) (D0355 breakdown G6, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: taking the newest transcript (the main thread's, as `run_state._newest_transcript` does) as the writer, so every subagent's verdict is attributed to the orchestrator
- AC2 must fail on: matching on the path alone, so a rewrite by the orchestrator after the reviewer's write is attributed to the reviewer
- AC3 must fail on: falling back to the main-thread transcript, or to the newest subagent transcript, when no write is found
- Checked on this machine's harness (Claude Code 2.1.292), re-checked 2026-11-12 on 2.1.318 with the same result: a subagent's transcript is `<projects>/<slug>/<session>/subagents/agent-<id>.jsonl`, with a `.meta.json` beside it (agentType, description, worktreePath, spawnedWithWorktree, toolUseId). Every record carries `sessionId` and `agentId`, and a Write tool_use carries `file_path` and `content`. `run_state._newest_transcript` (lib/run_state.py:867) still reads only the top-level `*.jsonl`; the meter's `_collect` (lib/run_state.py:1064) now reads the subagent files too, through `SUBAGENTS_DIR` and `SUBAGENT_GLOB` (lib/run_state.py:201-202). The panel confirmed a running Bash call is already in the transcript while it executes.
- A subagent's environment carries its parent's `CLAUDE_CODE_SESSION_ID` and `CLAUDE_CODE_CHILD_SESSION=1`, and no agent id (still so on 2.1.318), so session ids alone cannot tell an author agent from a reviewer agent. The transcript is the only witness.
- The briefed agent is the context whose earliest record of any kind carries the issued path: a prompt with the brief pasted in, or a later message handing the brief over as a file. A heredoc write appears as a Bash tool_use whose `command` holds the path and the bytes. Lines are filtered for the path string before any JSON is parsed, which bounds the scan.
- Checked at HEAD (2026-11-12): no criterion is met; lib/verdict_provenance.py does not exist and the `Source` cell is US1012's.
- US0986 is Done, so its dependency is dropped. Its harness selection is `token_meters.select` (lib/token_meters.py:149), where `SDLC_STUDIO_HARNESS` wins outright (lib/token_meters.py:52). Find the transcript folder as the meter does: `SDLC_STUDIO_TRANSCRIPTS` (`run_state.TRANSCRIPTS_ENV`, lib/run_state.py:161), else `run_state._harness_transcript_dir` (lib/run_state.py:895). Read them without editing lib/run_state.py, which US1149, US0998 and US0999 change in this run. The tests point `SDLC_STUDIO_TRANSCRIPTS` at a fixture folder, so no fixture is written under a real `~/.claude`.
- Existing tests this change reaches: test_critic.py holds the `show` listings (lines 1770-1788 and 3371-3385), and test_critic.py:1778 allows one line naming a unit per row.
- Reuses US0986's harness selection, with one provenance reader per harness. Claude comes first; every other harness answers `unknown`. Copy the fixture records' shape from a real transcript (LL0020). This covers CR0619 AC1's 'session id when known' and AC2's first half.

## Triage (2026-10-21)

Kept (D0387). To plan it:

- Marked 'Release: later' (D0356: 6.3).
- Depends on US1012 and US0986, both Draft.
- Notes pin the subagent transcript layout from Claude Code 2.1.292; re-pin from a current transcript at build (LL0020).
- Persona: User Story is 'As a team lead' (Jonah Reyes) while the field names Maya Okafor.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G6 after the refine panel's review |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
| 2026-11-12 | Claude Opus 5.5 (engineering seat) | Re-groomed at HEAD for run ten: US0986 dependency dropped (Done), transcript layout re-pinned on Claude Code 2.1.318, line references moved to HEAD, persona set to Jonah Reyes to match the story, release line set to run ten, Affects gains test_critic.py, fixture transcripts kept off the real home |
