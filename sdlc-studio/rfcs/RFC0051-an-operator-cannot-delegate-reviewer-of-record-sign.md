# RFC-0051: An operator cannot delegate reviewer-of-record sign-off to an agent: the trust boundary the guard requires cannot exist inside the authoring session

> **Status:** Draft
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py,.claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/reference-review.md
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Raised 2026-07-22 when the operator handed a 93-point run over to run unattended overnight and said an amigo could sign off on their behalf. The instruction is reasonable and the model has no way to honour it. `critic.record_signoff` supports a delegated form - principal, delegate, and a mandatory boundary described as 'another session, CI, another human' - and refuses a delegate that is the author or that appears as a recorded reviewer on the unit's own evidence or verdict rows, on the stated grounds that 'a delegate the author controls hollows out the self-approval guard'. Every agent the authoring session can spawn is by construction under the author's control. So a FRESH amigo, never recorded on those rows, passes the mechanical check while defeating the guarantee the check exists for, and the only thing standing between the two outcomes is whether the author happened to reuse a name. That is a gate whose enforcement rests on an accident of naming rather than on the property it means to test. The practical consequence is that unattended overnight delivery cannot reach Done at all on any project with `two_role_after` set, because Done requires a sign-off no unattended session may honestly produce - the work stops at reviewed-and-ready no matter how good it is. This was not resolved by picking an interpretation: the run built, verified and adversarially reviewed everything and left the signature unwritten.

## Design Options

- **A: accept the limit and make it explicit - an unattended run's best reachable state is reviewed-and-ready, sign-off is always deferred to a human, and the plan says so at plan time rather than the run discovering it at close**
- **B: an asynchronous sign-off channel - the run notifies the operator out of band (email, Telegram, a queued prompt) and blocks or parks until a real human answers, so delegation is to the operator's future self rather than to an agent**
- **C: a genuine external boundary - sign-off performed by a process the authoring session cannot brief or inspect, for example a CI job that reads only the committed evidence and applies fixed criteria, which is a real trust boundary rather than a differently-named subagent**
- **D: a scoped, recorded, expiring delegation - the operator pre-authorises agent sign-off for one named run, the ledger records that the delegate was author-controlled, and the row is marked provisional until a human countersigns**

## Recommendation

A plus C, and treat B as the near-term stopgap. A is honest today and costs nothing to state: naming the ceiling at plan time turns an unpleasant discovery at close into a known constraint, which is exactly what CR0354 asks the goal consult to do. C is the only option that produces a boundary the guard's own docstring would recognise, because it is defined by what the author CANNOT reach rather than by what the author promises not to touch. D is tempting and should be resisted in the form written above: a provisional row that is never countersigned decays into an ordinary one, and the project already has a lesson about self-reported evidence being indistinguishable from measurement once the label fades. If D is adopted at all, the provisional marking must block the release gate rather than merely annotate it.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Choose between: A: accept the limit and make it explicit - an unattended run's best reachable state is reviewed-and-ready, sign-off is always deferred to a human, and the plan says so at plan time rather than the run discovering it at close, B: an asynchronous sign-off channel - the run notifies the operator out of band (email, Telegram, a queued prompt) and blocks or parks until a real human answers, so delegation is to the operator's future self rather than to an agent, C: a genuine external boundary - sign-off performed by a process the authoring session cannot brief or inspect, for example a CI job that reads only the committed evidence and applies fixed criteria, which is a real trust boundary rather than a differently-named subagent or D: a scoped, recorded, expiring delegation - the operator pre-authorises agent sign-off for one named run, the ledger records that the delegate was author-controlled, and the row is marked provisional until a human countersigns | Open |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Filed |
