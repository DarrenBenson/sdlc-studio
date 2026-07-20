# CR-0371: sprint close should offer to file its blockers and close, rather than driving to a conclusion

> **Status:** In Progress
> **Decomposed-into:** EP0092
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md
> **Date:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Operator-reported, and reproduced live while filing it. A close that hits a blocker has exactly one route: fix the blocker. Each fix is real work, that work is committed, committing runs the gate, the gate or a review surfaces new findings, those findings become artefacts, and the new artefacts make the review anchor stale - which is itself a close blocker. The close chases a moving target and there is no bounded exit. Observed this session: closing one sprint produced six new artefacts and the discovery backlog went UP while the sprint was being closed. The specific trap is that some blockers are disproportionate to the unit: a one-line rsync exclude required a refine, an epic, a story with executable criteria, an independent review and an operator sign-off, because the close gate is uniform in a way the work is not. What is missing is the third option an operator would obviously want: acknowledge the blockers, FILE them as work, and close the sprint honestly with them recorded as outstanding - rather than either fixing everything or bypassing the gate.

## Impact

Every close that is not already clean, which in a live project is most of them. The operator watches a close that will not terminate and cannot tell whether it is progressing or spiralling; the pressure to reach for --no-verify grows with each cycle, which is exactly what an un-skippable gate is meant to prevent. It also inverts the point of the ceremony: the close stops being a record of what happened and becomes an obstacle course that reshapes the sprint while it runs.

## Acceptance Criteria

- [ ] Given a close with unmet blockers, when the close runs, then the operator is offered a bounded choice - fix them, or file them and close - rather than only the fix path
- [ ] Given the operator chooses to file and close, when the close completes, then each blocker is recorded as a real artefact linked to the run, and the run's outcome states plainly that it closed with known outstanding work
- [ ] Given the operator chooses to file and close, when the close completes, then nothing is silently waived: the retro and the review anchor both name what was deferred and why
- [ ] Given a blocker that is a hard correctness gate rather than an administrative one, when the operator chooses to file and close, then it is still refused - filing is for ceremony debt, never for a failing test or a red gate
- [ ] Given repeated close attempts, when a close is re-run, then it reports whether the outstanding set is shrinking or growing, so a spiral is visible rather than inferred

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Raised |
