# EP0205: A REJECT whose findings were repaired has a route back to covered, so a repaired batch stops reading like an unreviewed one

> **Status:** Done
> **Derived Point Total:** 18
> **Parent:** CR0506
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0506. Delivers the work CR0506 requested.

## Story Breakdown

- [x] [US0620: a REJECT can be answered by a recorded REPAIR naming the findings it closes and the evidence closing each](../stories/US0620-a-reject-can-be-answered-by-a-recorded.md)
- [x] [US0621: the coverage predicate distinguishes approved, repaired and unreviewed rather than two states](../stories/US0621-the-coverage-predicate-distinguishes-approved-repaired-and-unreviewed.md)
- [x] [US0622: a repair closing fewer findings than the REJECT raised is reported PARTIAL and names the outstanding ones](../stories/US0622-a-repair-closing-fewer-findings-than-the-reject.md)
- [x] [US0623: a finding closed by FILING is recorded distinctly from one closed by fixing](../stories/US0623-a-finding-closed-by-filing-is-recorded-distinctly.md)
- [x] [US0624: the close preflight states the three coverage counts separately](../stories/US0624-the-close-preflight-states-the-three-coverage-counts.md)

## Acceptance Criteria (Epic Level)

- [ ] A REJECT can be answered by a recorded REPAIR that names the findings it closes and the evidence closing each - the mutant re-applied, the test that now reddens, or the artefact the residue was filed as. The record is append-only on the same terms as a verdict, and it does not overwrite the REJECT: what the reviewer found stays true, and what was done about it becomes visible beside it.
- [ ] The coverage predicate distinguishes THREE states, not two: covered by an APPROVE, covered by a REJECT whose repairs are recorded, and not reviewed. A report that collapses the middle state into either of the outer two is the defect this is filed from - reading it as uncovered manufactures work, and reading it as covered would clear the gate on an unrepaired rejection.
- [ ] A repair record that closes fewer findings than the REJECT raised is reported as PARTIAL and names the outstanding ones, so a repair cannot be claimed wholesale over a rejection it only half answered. This is not hypothetical: the 18 units measured here include two whose residue (BG0401, BG0406) is still open and knowingly carried.
- [ ] A finding closed by FILING it as an artefact rather than by fixing it is recorded as such, with the artefact id, because 'fixed' and 'filed as a known issue' are different dispositions and the operator's rule is that both are legitimate - what is not legitimate is being unable to tell them apart afterwards.
- [ ] The close preflight's coverage line states the three counts separately. A single 'N covered by no independent review' figure was wrong by 18 out of 19 on the run that motivated this, and the reason it was wrong is that one number cannot carry three states.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
