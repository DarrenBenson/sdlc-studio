# CR-0754: routing.effort takes an effort per kind of unit, as routing.floor takes a tier, set from the bench's effort arm

> **Status:** In Progress
> **Decomposed-into:** EP0382
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_effort_setting.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Date:** 2026-11-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M89MN1 - raised during the run, 2026-11-25T21:34:18Z

## Summary

`routing.effort` sets one effort for every builder and one for every reviewer. The Claude-in-Foundry cost session recorded on 2026-11-24 (Controlling Claude Costs in Foundry) advised setting effort by the type of work rather than per request or for everything, and showed a published benchmark where Opus at medium scored about the same as max for roughly an eighth of the cost while Sonnet kept improving up to max: the right level depends on the work and has to be measured on your own tasks. This project's units differ in kind: prose and release paperwork, bugs that need a reproduction, and code changes.

Proposed: `routing.effort` accepts per-kind entries (for example docs, bug and code) beside the role defaults, the plan stamps the effort each unit resolved to, and the values are set from CR0710's bench effort arm rather than guessed. Depends on CR0710.

## Impact

A docs unit runs at the effort a code unit needs, or the reverse; with no per-kind setting the only lever is the whole run.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Raised |
