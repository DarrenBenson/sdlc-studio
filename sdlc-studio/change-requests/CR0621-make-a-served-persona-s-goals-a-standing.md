# CR-0621: Make a served persona's goals a standing, checkable criterion on the stories that touch them

> **Status:** In Progress
> **Consulted:** Dani Okafor, Lena Marsh, Sam Eriksson (2026-10-09)
> **Decomposed-into:** EP0285
> **Priority:** Medium
> **Type:** Feature
> **Size:** L
> **Affects:** .claude/skills/sdlc-studio/templates/persona.md, .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-persona.md, .claude/skills/sdlc-studio/scripts/tests/test_refine.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** homelab consuming project, 2026-10-07/08 (RUN-01M4B5HP drift-check sprint, RUN-01M4BZZ9 HA sprint), operator-approved after a session retrospective
> **Date:** 2026-10-08
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-08T11:05:55Z

## Summary

The homelab defines a 'Household Member' persona - 'affected by the platform without using it; their goals are a constraint on every production-tier story' - but nothing turns that constraint into a check. On 2026-10-08 the operator found the Master Bedroom wall switches no longer switched the lamps the morning after an HA sprint changed that room; the room stories' walk-tests were left 'owed by the operator', and no criterion anywhere said 'the physical controls in the changed room still work'. (The cause turned out to be Zigbee mesh routing, not the HA changes - which is exactly why the check must be on the outcome, not the diff.) Proposal: a served persona can declare standing criteria (e.g. `standing_criteria:` in its persona file, each with a Verify DSL line, scoped by a label/area/path match); `refine`/story creation seeds them into matching stories' Acceptance Criteria, and the seat review flags a matching story that lacks them.

## Acceptance Criteria

- [ ] A persona end goal can carry a Verify line, and the goal review brief lists the testable end goals the batch's served personas declare, so a goal that cannot be checked against them is named at plan

## Triage

- Confirmed: the persona template and `reference-persona.md` carry no standing criteria, so a served persona's goals become no check on any story.
- Priority Medium stands; Size L (a persona schema field, a Verify line scoped by area, and seeding or gating it onto matching stories). Related: CR-0623 (a story names the persona goal it serves) and BG0966 (`review_prep`'s persona usage) - the three change how persona goals reach a story and should be refined together.

## Further evidence (2026-10-08)

- Operator-relayed assessment of the agent-fleet project's run: make persona end goals testable (for example, a dependent system sees a persistent agent fault within N seconds), so the goal review can check a Sprint Goal against them mechanically at plan time. In that run the end goal surfaced halfway through the sprint, as a bug.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-08 | sdlc-studio | Raised |
| 2026-10-08 | Claude Opus 5.5 (triage) | Triaged: behaviour confirmed; Affects made repository paths; Size L; relations recorded |
| 2026-10-08 | Claude Opus 5.5 (triage) | Further evidence: testable persona end goals, checked at the goal review; AC added |

## Amigo Consult

_Consulted 2026-10-09: Dani Okafor (engineering, lead), Lena Marsh (product), Sam Eriksson (qa). Settle before building._

- Release cut: the panel recommends 6.2 for 19 points (End goal reader 3, goal review 3, plan advisory 3, Serves goal reference 3, --serves 2, goals-served 2, seat-card check 3), with the standing seed (5) later unless BG0995, G9's request-seed story and CR0628's breakdown story land first. Confirm.
- G7 interplay: should a standing criterion be exempt from revert-check naming? The panel recommends yes, as a seeded, reasoned `Revert-check-exempt` entry. The draft recommends instead that G7 exempt a criterion carrying the `standing:` marker. The field is one line whose single reason covers every id it lists (`revert_exemptions`, verify_ac.py:3926-3943), so a seeded id would either share an author's unrelated reason or overwrite it, and a hand-written standing AC counted by its verbatim Verify would still be named. Rule with G7.
