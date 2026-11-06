# CR-0681: Have the commit path write the Refs and Mentions trailers it now refuses for, make every tool that writes markdown emit lint-clean output, and print one line on success from the hooks and the commands agents filter by hand

> **Status:** In Progress
> **Decomposed-into:** EP0300
> **Parent:** RFC0062
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .githooks/commit-msg, .githooks/pre-commit, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/docgen.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_docgen.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** RFC0062 Phase 3, ceremony lens: finding 6; tool-output lens: finding 5
> **Date:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T12:23:42Z

## Summary

refusals.jsonl since 2026-10-06: message-refs 15, markdown 14 and gate 12 of 55 refusals; message-refs never names a defect, only attribution the Affects fields already hold (CR0659 relaxed it once). In run six 4 of 9 orchestrator commit calls were refused (message-refs twice, markdown, gate with markdown), the BG1213 landing three times in 7 minutes on the same 6 staged files, 684 s of 22 commit wall-minutes, and the markdown refusal surfaced BG1227 (`file_finding` writes a bare URL). Agents piped or redirected 578 of 700 shipped-command invocations (`verify_ac` run 30 of 33, self-check record 19 of 22, docgen 24 of 26, sprint.py lane 24 of 32), and the orchestrator hand-built land.sh, batch-land.sh and verdict.sh to quiet hook output; a direct commit prints 23 to 32 lines, 16 of them 'ok <lane>'. `lane land` and `lane accept` already keep commit output in commit.log (lib/lanes.py:127-141). Already true of the tree.

## Impact

Each refusal costs the orchestrator two to three calls and minutes of wall clock, and a `| tail -1` filter can hide why a command refused. The hooks are this repository's; the quiet success paths also serve consuming projects.

## Acceptance Criteria

- [ ] A prepare-commit-msg hook, or the lane-land commit step, appends Refs and Mentions trailers from the staged files' owning units, message-refs refuses only a trailer that contradicts ownership, and a replay of the BG1213 landing commits at the first attempt.
- [ ] `file_finding.py`, critic.py record and the retro output pass the markdown lane unedited, including when an argument carries a URL.
- [ ] On success the pre-commit and commit-msg hooks print one summary line, with the per-lane list on failure or under `SDLC_GATE_VERBOSE`=1; critic.py self-check record, `verify_ac.py` run, docgen.py surface and reading-guides and sprint.py lane return print at most two lines on success and the full reason on a refusal, pinned by a budget test.

## Recommendation

Derive trailers instead of refusing for them, clean the producers' markdown, and add quiet success paths. Saving 0.25M per run: 4 refusals x 2.5 calls survive the drive loop as judgement turns, at about 20k a call once the wave-session and sprint-drive CRs land = 0.20M (0.47M at run six's 47k), plus about 0.05M of tool-output's 0.15M for quiet output (the wrapper writing it counts goes with the drive loop, and the rest is carried by fewer calls in wave sessions); plus about 11 minutes of wall clock per run. Risks: attribution is unchanged because the trailers come from the same staged-file-to-Affects map; the markdown lane stays the backstop for hand-written files; a budget test must keep every failure path verbose.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Raised |
