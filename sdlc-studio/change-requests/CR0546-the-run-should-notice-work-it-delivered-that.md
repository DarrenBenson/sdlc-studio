# CR-0546: the run should notice work it delivered that its batch never named

> **Status:** In Progress
> **Decomposed-into:** EP0237
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/close_owed.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py
> **Date:** 2026-08-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

A batch is approved once at plan time and thereafter only READ. Work agreed after that point - a sweep the operator asks for mid-run, repairs a review round demands, a fix instructed during a close - is delivered, reviewed and signed off without ever joining the batch, and nothing notices. Twelve units reached a terminal status that way across two consecutive runs, and BOTH runs closed green: the close checks that the batch is accounted for, never that the account is the whole of what shipped. `close_owed detect` finds it afterwards, which is the right backstop and the wrong moment - by then the run that caused it has closed and the account has to be reconstructed from git.

## Impact

Every run that takes on work mid-flight, which is most of them. The damage is not to the code - the units were built and reviewed properly - it is that the run's own record understates what it did, so velocity, cost-per-point and scope-creep figures are all computed over a batch that is not what shipped. RETRO0104 exists solely to reconstruct one such gap.

## Acceptance Criteria

- [ ] Given an open run, when a unit not in its batch reaches a terminal status, then the transition reports it and names the command that would add it
- [ ] Given an open run, when a unit IN its batch reaches a terminal status, then nothing is reported - the prompt must not fire on the normal path
- [ ] Given a run closing with units delivered outside its batch, when the close runs, then it reports them as a non-blocking row naming each id

## Recommendation

Ask the question at DELIVERY rather than at the next close. When a unit transitions to a terminal status while a run is open and its id is not in the run's batch, `transition` should say so and name `sprint batch --add <id> --reason '<why>'` - a prompt, not a refusal, because taking on agreed work mid-run is legitimate and the fix is one command. Consider having the close report the same set as a non-blocking row, so a run that ends with unbatched deliveries states it rather than leaving it for a later detector. The three shapes worth handling distinctly: work the operator agreed mid-run, repairs raised by a review round (three of the twelve, and the systematic case), and work delivered by the close itself (one of the twelve), which no batch could have named in advance.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-17 | sdlc-studio | Raised |
