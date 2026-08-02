# CR-0526: a sprint ends with nothing open - a non-stop-ship finding becomes a bug and its story closes

> **Status:** In Progress
> **Decomposed-into:** EP0206
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** human
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/close_guard.py, .claude/skills/sdlc-studio/scripts/transition.py
> **Priority:** Critical
> **Type:** Improvement
> **Size:** M

## Summary

The operator's rule, stated during the RUN-01KYZKY5 close and found to be written nowhere: a review finding that is not stop-ship is opened as a NEW BUG, and the original story is CLOSED with a pointer to it. A sprint may not end with any unit open, because the code ships at the end of the sprint - the work moves to the bug, not the story.

Searched before filing. `stop-ship` exists as a ruling vocabulary for findings CARRIED into a retro (reference-sprint.md:298), and a stop-ship ruling holds the close. Nothing states the converse - what happens to a non-stop-ship finding, or that a story carrying one should close. Nothing requires a sprint to end with no open units. `close_guard` imposes no requirement on a non-terminal unit at all.

The cost of it being unwritten was paid twice in one close. Nineteen delivered, rejected units were first left in `Review`, and when the operator asked for that to be cleared they were moved to `Ready` - both wrong, and neither refused by anything. The rule reached the agent only because the operator said it out loud, which is the least reliable channel there is.

## Impact

This changes what a sprint close MEANS, so leaving it unwritten leaves the central ceremony ambiguous. It also decides where work lives between sprints: a rejected story left open is invisible backlog that no bug tracks and no plan selects, while a closed story plus a filed bug is work the next plan can actually pick up. And it is the difference between a release that ships with known defects RECORDED and one that ships with them attached to a story nobody re-reads.

LL0027 applies with full force - this is a rule that matters, it is enforced by nothing, and the agent that broke it had read every governing document in the repository.

## Relationship to CR0506

Found after filing, and they are complementary rather than duplicates. `CR0506` supplies the
missing STATE - a REJECT whose findings were repaired has no route back to covered, so the
coverage predicate cannot tell "reviewed, rejected, repaired" from "never looked at". This CR
supplies the RULE and the GATE - what happens to a non-stop-ship finding, and a close that
refuses while any batch unit is open.

Neither closes without the other. Without `CR0506` the state does not exist, so every close of
a rejected-then-repaired batch needs a waiver sweep; without this CR the rule stays unwritten
and unenforced, which is how RUN-01KYZKY5 left 19 units open twice in one close.

`CR0506` was filed 2026-07-30 and is still Proposed. It has now cost three closes in four days:
D0077-D0087 (11 units), D0092-D0103 (12 units), and this run's 18 - **41 units waived on one
rule**. That number is the argument for building it.

## Acceptance Criteria

- [ ] The doctrine states the rule: a non-stop-ship finding is filed as its own artefact and the story closes pointing at it; a stop-ship finding holds the close
- [ ] `sprint close` and `sprint stop` REFUSE while any batch unit is in a non-terminal status, naming each one and the artefact its findings moved to - the refusal is what makes the rule real rather than remembered
- [ ] Closing a story over a recorded REJECT requires the finding to have somewhere to live: a filed artefact id, or an explicit stop-ship ruling that holds the close instead
- [ ] The stop-ship judgement is recorded per finding at review time rather than inferred at the close, so the close reads a decision somebody made instead of making one for them
- [ ] A story closed this way names the bug in its own record, so a reader of the story learns where the work went without consulting the retro

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
