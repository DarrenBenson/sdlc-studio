# BG0969: sprint close --file-and-close silently drops a supplied --goal-verdict, then refuses because the goal is unjudged - a hard blocker it cannot file

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_close_file_and_close_goal_verdict.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG0969.md
> **Evidence:** Found running a consuming project on the installed skill 6.1.0, 2026-10-07; confirmed by reading the code at sdlc-studio main fb1ce886.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T12:36:59Z

## Summary

`cmd_close` (sprint.py ~8957) sets `supplied = args.goal_verdict if args.goal_verdict and args.note and not filing else None` - the --file-and-close path deliberately records no verdict. The pre-flight then reports '[goal-verdict] the Sprint Goal is unjudged' and the goal-judged checklist row as a HARD blocker, so `--file-and-close --goal-verdict achieved --note ...` is refused. Nothing says the flag was ignored; the operator re-reads a command that looks complete. With a goal stated at plan time, --file-and-close cannot succeed unless `sprint.py goal-verdict` was run separately first.

## Steps to Reproduce

On an open run with a sprint goal: `sprint.py close --retro <id> --file-and-close --goal-verdict achieved --note x` -> pre-flight 'the Sprint Goal is unjudged' and file-and-close REFUSED on goal-judged.

## Proposed Fix

Either record the supplied verdict on the file-and-close path too (it is an answer, not ceremony), or refuse up front with 'run sprint.py goal-verdict first: --goal-verdict is ignored with --file-and-close'.

## Acceptance Criteria

- [ ] **AC1** --file-and-close with --goal-verdict and --note either records the verdict or refuses up front naming the flag it ignored
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_file_and_close_goal_verdict.py -k supplied_verdict_not_silently_dropped

## Triage

- Reproduced at 8b844a80 by the code path: `cmd_close` sets `supplied` to None whenever `filing` (sprint.py:8959). Already in the code since BG0800 (6bdde35f, 2026-09-27); not a regression.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | Claude Opus 5.5 | Filed |
| 2026-10-07 | Claude Opus 5.5 (triage) | Triaged: reproduced at 8b844a80, not a regression, consuming-project name generalised for the neutrality lane; changelog fragment added to Affects |
