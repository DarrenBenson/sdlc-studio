# CR-0629: A served persona's testable End goal is run at the close as evidence for the goal verdict

> **Status:** In Progress
> **Consulted:** Dani Okafor, Lena Marsh, Sam Eriksson (2026-10-12)
> **Decomposed-into:** EP0287
> **Priority:** Medium
> **Type:** Feature
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/persona_goals.py, .claude/skills/sdlc-studio/scripts/tests/test_goal_verdict_end_goal_evidence.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Raised by the G11 breakdown of CR0621 and its panel review (D0355); framed by RFC0061 workstream 4.
> **Date:** 2026-10-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-09T10:05:23Z

## Summary

The goal review names the testable End goals a Sprint Goal traces to (G11), but nothing runs them. At the close, the goal verdict judges the increment against the seats' `done_means` alone, so a goal whose End goal Verify is still red can be closed as met. Run each traced persona's executable End goal Verify at the close (and optionally at plan, to show it red before the work) and record the result beside the goal verdict: the served-goal outcome evidence RFC0061's D4 and D6 name for user personas learning from usage. Framed by RFC0061 workstream 4; decide its strength (reported or refusing) there. Depends on G11's End goal reader and goal review stories.

## Impact

A Sprint Goal can be closed as met while the persona End goal it traces to still fails.

## Acceptance Criteria

- [ ] Given a Sprint Goal that traces to a persona whose End goal carries an executable Verify, when the run closes, then the goal verdict records that Verify's result beside the seats' `done_means`, and a red result is reported by name rather than read as met.

## Triage (2026-10-21)

Kept (D0387). To plan it:

- Stakeholder consult on EP0287 (D0374)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | Claude Opus 5.5 | Raised |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |

## Amigo Consult

_Consulted 2026-10-12: Dani Okafor (engineering, lead), Lena Marsh (product), Sam Eriksson (qa). Settle before building._

- Precision bar for a seat's miss (D0364 ruling 3): the draft sets at least 8 of a fresh 12-pair sample, judged by a seat other than the builder, before the rule ships. Confirm or set another bar.
- Size: the revision is 92 points against the draft's 68 (the operator's two additions are 13; the panel's required changes 11). Confirm 6.2 whole, or apply the cut order in the recommendation.
