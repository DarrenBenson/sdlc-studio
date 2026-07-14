# BG0141: retro extract titles a lesson from its first LINE, so a wrapped lesson gets a title cut mid-sentence

> **Status:** Open
> **Severity:** Low
> **Effort:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

retro.py extract lifts a `## Lessons` bullet into the project store and titles it from the bullet first LINE, not its first SENTENCE. A lesson written across several wrapped lines therefore gets a title truncated at the wrap point: L-0028 reads "A plausible story fitted to a real pattern is not a finding. This retro originally recorded that" and L-0027 reads "Before tuning a coefficient, check that its input correlates with the target at all. The cost". Those truncated titles are exactly what `sprint plan` prints as the lessons digest at the top of every plan - the surface the whole learning loop exists to serve, and the one an agent under effort pressure reads instead of opening the file. A lesson whose headline stops mid-clause is a lesson that will be skimmed past. The store is fine; the headline is mangled.

## Steps to Reproduce

1. Write a retro `## Lessons` bullet longer than one wrapped line. 2. Run retro.py extract --id RETROxxxx. 3. Read sdlc-studio/.local/lessons.md: the `## L-00NN:` heading is the bullet first physical line, cut wherever the author happened to wrap it. 4. Run sprint.py plan and read the "lessons in force" digest: the truncated headline is what the next sprint is shown.

## Proposed Fix

Title the lesson from its first SENTENCE (split on the first full stop followed by a space, with a sensible max length and an ellipsis), not its first line - and normalise the wrap first, so the title is independent of where the author happened to break the line. The body should keep the full text. Guard it with a test that writes a bullet wrapped mid-sentence and asserts the stored title is the complete sentence, since this defect is invisible unless a lesson happens to be long.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |
