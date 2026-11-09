# BG1327: A verdict file's `\;` escape, which the review brief prescribes for a semicolon inside a finding, still splits the finding when `critic.py record --from-verdict` reads it, leaving an untagged piece the record refuses

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** US1142-verdict-r1 first record refusal (RUN-01M7061X)
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T19:04:41Z

## Summary

Hit recording US1142's verdict in run nine (2026-11-09). The brief tells a reviewer to escape a `;` inside a finding as `\;`. In a verdict file read with `--from-verdict FILE`, the escaped semicolon still split the finding in two, and the second piece carried no origin tag, so `critic.py record` refused the whole verdict ('these findings carry no origin'). The reviewer had to replace the semicolon with a full stop.

## Steps to Reproduce

1. Write a verdict file whose finding is `[pre-existing] so nothing here is wrong\; this is offered`.
2. Run `critic.py record --unit <id> --from-verdict <file> ...`: it refuses an untagged finding.

## Proposed Fix

Honour `\;` as a literal semicolon in the --from-verdict parser, as the brief promises, and add a test that an escaped semicolon keeps one finding whole beside an unescaped one that splits.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Hit recording US1142's verdict in run nine (2026-11-09).
- [ ] **AC2** The proposed fix lands, pinned by a test: Honour `\;` as a literal semicolon in the --from-verdict parser, as the brief promises, and add a test that an escaped semicolon keeps one finding whole beside...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
