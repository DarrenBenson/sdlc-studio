# CR-0623: The story template's Persona Reference section is boilerplate - require it to name the goal served, or drop it

> **Status:** In Progress
> **Consulted:** Dani Okafor, Lena Marsh, Sam Eriksson (2026-10-09)
> **Decomposed-into:** EP0285
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

## Amigo Consult

_Consulted 2026-10-09: Dani Okafor (engineering, lead), Lena Marsh (product), Sam Eriksson (qa). Settle before building._

- Release cut: the panel recommends 6.2 for 19 points (End goal reader 3, goal review 3, plan advisory 3, Serves goal reference 3, --serves 2, goals-served 2, seat-card check 3), with the standing seed (5) later unless BG0995, G9's request-seed story and CR0628's breakdown story land first. Confirm.
- G7 interplay: should a standing criterion be exempt from revert-check naming? The panel recommends yes, as a seeded, reasoned `Revert-check-exempt` entry. The draft recommends instead that G7 exempt a criterion carrying the `standing:` marker. The field is one line whose single reason covers every id it lists (`revert_exemptions`, verify_ac.py:3926-3943), so a seeded id would either share an author's unrelated reason or overwrite it, and a hand-written standing AC counted by its verbatim Verify would still be named. Rule with G7.
