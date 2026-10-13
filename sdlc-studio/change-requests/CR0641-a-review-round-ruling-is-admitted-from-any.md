# CR-0641: A review-round ruling is admitted from any accepted decision about the unit, not one that authorises a round

> **Status:** Proposed
> **Priority:** P3
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_decisions.py
> **Evidence:** BG1003 round-1 QA verdict (sdlc-studio/reviews/critic-verdicts.md), finding 3: D0351 and D0354 each admitted a round on BG0993 (executed, rc 0). The rule as documented (subject = first id) admits them by design.
> **Date:** 2026-10-13
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-13T14:45:52Z

## Summary

`critic.py record --ruling DNNNN` admits one review round past `review.max_rounds` when the decision is accepted, standing, names the unit first and has not authorised a round before (BG1003). Nothing in that test asks whether the decision authorises a round at all. On this repository's own log, D0351 (fast-track BG0993) and D0354 (BG0993 ships and stays Open) each admitted a round on BG0993 when the BG1003 QA seat executed them, so BG0993 holds four usable rulings for the two rounds D0352 and D0353 authorise. The operator who passes --ruling is accountable for choosing the right decision, but the tool cannot tell a round authorisation from any other ruling about the unit.

## Impact

An operator, or an agent acting for one, can lift the review cap with a decision that never authorised a further round, as long as it is about the unit. The cap is the review loop's backstop, so the authorisation it accepts should be one written for that purpose.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Recommendation

Require a structured subject (`decisions.py rule --subject review-round:<unit>`), keeping first-id prose decisions readable for the decisions already on file (D0352, D0353) through a dated cut-over.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-13 | sdlc-studio | Raised |
