# EP0201: A suite verdict is a fact read from a file, never a stream an agent interprets

> **Status:** Done
> **Derived Point Total:** 8
> **Parent:** CR0519
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0519. Delivers the work CR0519 requested.

## Story Breakdown

- [x] [US0610: tools/run-suite.sh runs a suite and writes exit_code, counts, duration and head_sha to sdlc-studio/.local/suite-verdict.json, printing only the verdict line](../stories/US0610-tools-run-suite-sh-runs-a-suite-and.md)
- [x] [US0611: A greenness claim whose verdict file is absent or stale against HEAD is refused by the commit gate](../stories/US0611-a-greenness-claim-whose-verdict-file-is-absent.md)

## Acceptance Criteria (Epic Level)

- [ ] `tools/run-suite.sh <scripts|tools|all>` runs the suite and writes {suite, `exit_code`, passed, failed, duration, `head_sha`} to sdlc-studio/.local/suite-verdict.json.
- [ ] It prints only the verdict line, so there is nothing worth piping to `tail` and the incentive that causes the masking is removed rather than resisted.
- [ ] A non-zero suite writes a verdict recording the failure - a red run must not leave a file that reads as green, or the wrapper reproduces the defect it replaces.
- [ ] The verdict records the HEAD sha it was taken at, so a stale verdict is distinguishable from a current one.
- [ ] The commit gate refuses a greenness claim whose verdict file is absent or stale against HEAD, so the rule is enforced by the command people run rather than stated in AGENTS.md (LL0027).
- [ ] A test pins that a failing suite produces `exit_code` != 0 in the file - the mutant is a wrapper that always writes zero.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
