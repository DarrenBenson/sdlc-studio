# CR-0464: Lessons accumulate faster than they are read: curate a top few at each retro and make them a read gate for the sprint and its reviewers

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/../reference-agentic-lessons.md
> **Date:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (operator-proposed, evidenced by four violations of a recorded scar in one night); agent; skill v5.0.0

## Summary

252 open lessons sit in the summary. The plan already ranks and prints a digest, and lessons are STILL ignored - not for want of surfacing but because a ranked list of 252 is not something a working agent reads and holds. The evidence is direct and embarrassing: the recorded scar 'a test rename is cross-unit coupling' was violated four times in a single repair, by the author who filed it, on the same night; and LL0013 (an enumerated list silently exempts what it forgot), cited 23 times, was violated at least four more times across two sprints.

The operator's proposal is that the RETRO curate a small set - five or so - of the lessons that matter MOST right now, written as a summary rather than a ranking, and that this summary be READ at the start of a sprint and by the reviewers. That makes learning a cycle with a gate in it: record, curate, read, apply, re-curate. A ranking is a fact about the past; a curated top five is a decision about what to carry into the next batch.

The second half of the proposal is the sharper one: a lesson that keeps being violated should be able to PROPOSE a change request or a bug to the operator. A lesson violated repeatedly is not a memory problem, it is a missing guard, and the loop should turn it into work rather than into a louder note.

## Impact

Who: every sprint and every reviewer, in this project and in every consuming one - the learning loop is one of the skill's central claims. What breaks today: lessons are written diligently, ranked automatically, printed at plan time, and then not applied, so the cost of learning is paid and the benefit is not collected. Each repeat costs a review round and a repair cycle - the direct cause of a five-hour estimate taking seven. Curation without a read gate would change nothing, and a read gate over 252 items is unreadable, so the two halves only work together.

## Acceptance Criteria

- [ ] The retro produces a curated summary of the few lessons that matter most for the NEXT batch - a written judgement, not a ranking - and the retro's content check requires it.
- [ ] The sprint reads that summary at plan time and carries it into every delivery lane's brief, so it reaches the agent doing the work rather than only the operator watching.
- [ ] The reviewers receive it too, so the pass most likely to catch a repeat is told what has been repeating.
- [ ] A lesson violated again after being carried is reported at the close, naming the unit that repeated it - a repeat is evidence the lesson needs a guard, not a louder note.
- [ ] A lesson that has been repeatedly violated can propose a change request or bug for the operator to accept or decline, so the loop ends in work rather than in a longer list.
- [ ] The curated set is re-decided each retro rather than accumulating, so it stays small enough to be read and current enough to be worth reading.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (operator-proposed, evidenced by four violations of a recorded scar in one night) | Raised |
