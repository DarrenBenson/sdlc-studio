# CR-0623: The story template's Persona Reference section is boilerplate - require it to name the goal served, or drop it

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Feature
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/templates/core/story.md, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/review_prep.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py, .claude/skills/sdlc-studio/scripts/tests/test_review_prep.py
> **Evidence:** homelab consuming project, 2026-10-07/08 (RUN-01M4B5HP drift-check sprint, RUN-01M4BZZ9 HA sprint), operator-approved after a session retrospective
> **Date:** 2026-10-08
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-08T11:06:04Z

## Summary

Across the homelab's stories the 'Persona Reference' block is the same two lines copied in ('**Operator** - The homelab owner... [Full persona details]'), carrying no information about which of the persona's goals the story serves; `review_prep`'s `persona_usage` then counts it as use (see BG0966 for the inverse problem). A section that is always identical is noise the seats learn to skip. Proposal: the template asks for `Serves: <persona> - <goal id or quoted goal>`, validate warns when it is absent or a verbatim copy of the persona's summary, and `persona_usage` counts a persona as used only through a named goal.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Triage

- Confirmed: `templates/core/story.md` carries a `### Persona Reference` section filled as a fixed block, and BG0966 (Open) is the inverse defect in `review_prep`'s persona usage count.
- Priority Medium stands; Size S (template, a validate warning, and the usage count reading a named goal). Related: CR-0621 and BG0966; refine together.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-08 | sdlc-studio | Raised |
| 2026-10-08 | Claude Opus 5.5 (triage) | Triaged: behaviour confirmed; Affects made repository paths; Size S; relations recorded |
