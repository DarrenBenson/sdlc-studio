# CR-0506: a REJECT whose findings were all repaired has no route back to covered, so a fully repaired batch reads identically to one nobody reviewed

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py
> **Date:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio agent (Claude Opus 5); human; v1
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

`critic.sprint_covers_independently` is satisfied only by an APPROVE. There is no state for a REJECT whose findings have since been repaired: no verb records the repair against the verdict, and nothing re-runs the reviewer. So the coverage predicate reports a batch that was independently reviewed, rejected, repaired and mutation-verified as UNCOVERED - the same word it uses for a unit no reviewer ever opened. Measured on RUN-01KYPZ1G (44 units): the close preflight reported '28 of 44 unit(s) are covered by no independent review'. Reading the ledgers, 18 of those 28 carry a REJECT from a real independent subagent reviewer, every finding of which was repaired in-run and verified by re-applying the reviewer's own mutant, with the residue filed as bugs (BG0401 and BG0406 carried knowingly, seven others reaching Fixed). Only one of the 28 - US0465 - was genuinely delivered and never reviewed. The number was wrong by 18 out of 19, and it was wrong in the direction that hides the single real gap inside a crowd of false ones.

## Impact

Who: anyone reading a coverage figure to decide whether a run can close, and the next agent inheriting the residue. What breaks: the figure cannot discriminate the two states an operator most needs told apart - 'reviewed, rejected, repaired' and 'never looked at'. The practical consequence is worse than an inaccurate number: the honest response to 28 uncovered units is a waiver sweep or a re-review sweep, and both spend real effort on the 18 that need neither, while the one unit that does need a review is indistinguishable inside the total. It also pushes an operator towards the waiver route for units whose findings were in fact fixed, which writes a weaker record than the truth. This is the second time in two days the same missing state has cost a close: the 11 waivers D0077-D0087 recorded on the 2026-07-30 batch were recorded for exactly this reason, and their stated rationale names it.

## Acceptance Criteria

- [ ] A REJECT can be answered by a recorded REPAIR that names the findings it closes and the evidence closing each - the mutant re-applied, the test that now reddens, or the artefact the residue was filed as. The record is append-only on the same terms as a verdict, and it does not overwrite the REJECT: what the reviewer found stays true, and what was done about it becomes visible beside it.
- [ ] The coverage predicate distinguishes THREE states, not two: covered by an APPROVE, covered by a REJECT whose repairs are recorded, and not reviewed. A report that collapses the middle state into either of the outer two is the defect this is filed from - reading it as uncovered manufactures work, and reading it as covered would clear the gate on an unrepaired rejection.
- [ ] A repair record that closes fewer findings than the REJECT raised is reported as PARTIAL and names the outstanding ones, so a repair cannot be claimed wholesale over a rejection it only half answered. This is not hypothetical: the 18 units measured here include two whose residue (BG0401, BG0406) is still open and knowingly carried.
- [ ] A finding closed by FILING it as an artefact rather than by fixing it is recorded as such, with the artefact id, because 'fixed' and 'filed as a known issue' are different dispositions and the operator's rule is that both are legitimate - what is not legitimate is being unable to tell them apart afterwards.
- [ ] The close preflight's coverage line states the three counts separately. A single 'N covered by no independent review' figure was wrong by 18 out of 19 on the run that motivated this, and the reason it was wrong is that one number cannot carry three states.

## Recommendation

The repair record belongs beside the verdict in `critic.py`, not in a new ledger - the whole value is that a reader of the verdict sees the disposition without knowing to look elsewhere. Sequence it BEFORE the next close rather than after: the gap has now cost two consecutive runs, and the second time it produced a report that would have sent an operator to waive 18 units whose findings were already fixed and mutation-verified. Check during refine whether this subsumes the waiver route for this case entirely - a waiver records that a gate was knowingly bypassed, and a repaired rejection is not a bypass, so reaching for `decisions.py waive` here (as D0077-D0087 did) writes a weaker and less accurate record than the facts support.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | sdlc-studio agent (Claude Opus 5) | Raised |
