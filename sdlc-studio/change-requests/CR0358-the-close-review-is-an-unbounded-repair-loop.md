# CR-0358: the close review is an unbounded repair loop: no convergence check, no cost ceiling, and the author writes the reviewer's prompt

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-review.md
> **Date:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The close review is an unbounded repair loop with no convergence guarantee, no cost ceiling and no circuit breaker. RUN-01KXVYGR took FIVE rounds. Round 1 earned its keep: six false negatives across three production files, including one that destroyed a Date cell on every apply and a metrics gate whose recorded baseline was a measurement of its own blind spot. Rounds 2, 3 and 4 were different in kind - each round's MAJOR was CREATED BY the previous round's repair, all three in the same 40-line function, and the review was paying to catch defects the repair loop was manufacturing. Nothing in the process noticed that. A model less able to hold five rounds of context, or less willing to concede, could loop here indefinitely, and the token cost is roughly 80k per review round before the repair work that follows each one. Three separate faults. There is no repair-regression detector: a finding landing in code the PREVIOUS round touched is a different signal from a fresh finding, and should stop the patching rather than feed it. There is no round ceiling or cost surface, so nobody is asked whether the next round is worth buying. And the author writes the reviewer's prompt, so it can be primed - the rounds 4 and 5 briefs both opened by asserting the pattern would continue, which biases toward REJECT and inflates confidence in the pattern being claimed.

## Impact

Any project running this loop can burn unbounded tokens on rounds whose findings its own repairs are creating, with no signal that the repairs are the cause. A weaker or more deferential model may not escape at all. The operator is never shown the cost or asked whether the next round is worth it, and the reviewer's independence is only as good as a prompt the author wrote.

## Acceptance Criteria

- [ ] the review loop counts its rounds on the run state and refuses to start another past a configured ceiling without explicit operator confirmation
- [ ] a finding located in code the previous round's repair touched is reported as a repair regression, distinctly from a fresh finding
- [ ] on a repair regression the loop escalates to a revert / redesign / accept-and-file decision instead of another patch round
- [ ] cumulative review token cost is recorded per round and shown when the next round is offered
- [ ] the reviewer brief is generated from a neutral template that carries the diff and risk surface but not the prior verdicts, the round number, or any expected conclusion

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Raised |
