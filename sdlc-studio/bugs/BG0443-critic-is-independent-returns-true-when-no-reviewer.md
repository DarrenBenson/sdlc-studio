# BG0443: critic.is_independent returns True when no reviewer is recorded at all, so an unreviewed row satisfies the predicate four gates depend on

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** engineering amigo seat (independent, isolated worktree); human; v1
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

`critic.is_independent` ends `return bool(author) and reviewer != author`. It never tests that a reviewer EXISTS. An empty reviewer is not equal to a recorded author, so the expression is True and the row passes as independently reviewed. The docstring claims the opposite - that the unit was "authored and reviewed by distinct identities" - so the function is documented correctly and implemented incorrectly. `record_verdict` floors an empty author to `-` but gives the reviewer no such floor, which is what lets the empty value reach the ledger in the first place.

## Steps to Reproduce

Executed at d7a1ad8f, 2026-07-30:

```text
python3 -c "import sys; sys.path.insert(0,'.claude/skills/sdlc-studio/scripts'); import critic; print(`critic.is_independent(`{'verdict':'APPROVE','reviewer':'','author':'alice'}))"
True
```

End-to-end through the writer, `record_verdict(root,'US0001','APPROVE',reviewer='',author='alice')` writes the row `| US0001 | APPROVE |  | alice | 2026-07-30 | - |` and `is_independent(verdict_for(...))` returns True over it.

Four gate consumers use the predicate alone: `plan_review.py:191`, `repair_plan.py:270`, `project_upgrade.py:679`, `conformance.py:317`.

NOT currently live: a sweep of `critic-verdicts.md` and `critic-evidence.md` at this revision finds ZERO rows with an empty reviewer, so no unit in this workspace is presently cleared by the hole. It is latent, which is why it is filed as a carried issue rather than held. Found by the engineering amigo seat during the close of RUN-01KYPZ1G; the liveness sweep was run by the author before filing.

## Proposed Fix

Require the reviewer: `return bool(author) and bool(reviewer) and reviewer != author`. Floor the reviewer in `record_verdict` the same way the author is floored, so the empty value cannot reach the ledger. Pin both with a test asserting an empty reviewer is refused at the writer AND rejected by the predicate - the predicate alone is not enough, since the writer is what made the bad row reachable. A guard that fails OPEN is the direction this project's design says a guard must never fail.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `critic.is_independent` ends `return bool(author) and reviewer != author`.
- [ ] Following the recorded steps no longer reproduces the defect: Executed at d7a1ad8f, 2026-07-30: End-to-end through the writer, `record_verdict(root,'US0001','APPROVE',reviewer='',author='alice')` writes the row `| US0001...
- [ ] The proposed fix lands, pinned by a test: Require the reviewer: `return bool(author) and bool(reviewer) and reviewer != author`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | engineering amigo seat (independent, isolated worktree) | Filed |
