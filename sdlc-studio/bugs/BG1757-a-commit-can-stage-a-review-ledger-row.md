# BG1757: A commit can stage a review-ledger row whose ruling cites a decision the commit does not carry

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_ledger_lints.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** run twenty-six (RUN-01M87B5M): origin/main at 772b468d3 held two critic-verdicts rows citing D0626 and D0627 while its decisions.md held neither
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M87B5M - raised during the run, 2026-11-25T08:36:09Z

## Summary

`critic.py record --ruling D` checks that D is a row in the working tree's decisions.md, but no commit lane checks the staged pair. In run twenty-six two paperwork commits staged critic-verdicts.md rows citing D0626 and D0627 without decisions.md, and the push carried them, so origin/main held ledger rows citing rulings it did not have until a later commit added them.

## Steps to Reproduce

1. `decisions.py add` a ruling, then `critic.py record --ruling <id>`.
2. Stage sdlc-studio/reviews/critic-verdicts.md but not sdlc-studio/decisions.md, and commit.
3. The commit passes; `git show HEAD:sdlc-studio/decisions.md` lacks the cited id.

## Proposed Fix

Have the commit's ledger lane read the staged decisions.md and refuse a staged verdict row whose ruling it does not hold.

## Acceptance Criteria

- [ ] **AC1** Given a staged review-ledger row whose ruling names a decision the staged decisions.md does not hold, when the commit runs, then it is refused with the decision id named. Fails on: the commit passing.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Filed |
