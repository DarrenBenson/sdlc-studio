# BG0354: Three more places still enumerate the v2 four-digit id, so a v3 ULID unit silently escapes them

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .githooks/commit-msg
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction); agent; skill v5.0.0

## Summary

BG0318 closed this in conformance.py. The same hole survives in sprint.py's `reachable_end_state` (a fail-open, so a ULID unit is reported reachable when it is not) and in .githooks/commit-msg's paste-ready Refs hint, which prints a WRONG id for a ULID unit rather than none. Same LL0013 class, third and fourth instances.

## Steps to Reproduce

Measured against the current tree, not read. With sdlc-studio/.config.yaml containing 'review:\n  `two_role_after`: US0100\n':

  `sprint.reachable_end_state(root`, [{"id": "US0101"}])       -> Review | derived from the cuto; Reproduced directly at the shell:

  $ printf 'US01010 US01011: batch\n' | grep -oE '(US|BG|CR)-?[0-9]{4}' | tr -d '-'
  US0101
  US0101

  $ printf 'US-01JQK3F8 BG-01JQK4Z2: batch\n' | grep -oE '(US|BG|CR)-?[0-9]{4}' |

## Proposed Fix

See the summary; each cited site names its own remedy.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction) | Filed |
