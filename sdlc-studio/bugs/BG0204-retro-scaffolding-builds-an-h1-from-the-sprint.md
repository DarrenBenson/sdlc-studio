# BG0204: retro scaffolding builds an H1 from the Sprint Goal without stripping its trailing full stop

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/artifact.py
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

sprint close with no --retro scaffolds the batch retro and titles it from the run's Sprint Goal. A Sprint Goal is a sentence and ends in a full stop, so the generated H1 does too, and markdownlint MD026 (no-trailing-punctuation in heading) blocks the very commit that carries the retro. This is BG0179's defect in a second generator: handoff.generate was fixed to strip trailing punctuation from a goal-derived H1, and the retro scaffolding path was not. Hit at the RUN-01KXVYGR close, where the close-paperwork commit was blocked and the H1 had to be corrected by hand before it could land.

## Steps to Reproduce

1. Open a run whose --sprint-goal ends in a full stop. 2. Run sprint.py close with no --retro so it scaffolds. 3. Read line 1 of the generated retro: the H1 ends in '.'. 4. Run markdownlint over it and observe MD026.

## Proposed Fix

Strip trailing punctuation when deriving the retro H1 from the Sprint Goal, reusing whatever handoff.generate does for the same job rather than growing a second implementation. Add a regression test with a goal sentence ending in a full stop, asserting the H1 does not, and check any other generator that titles an artefact from a prose field.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Filed |
