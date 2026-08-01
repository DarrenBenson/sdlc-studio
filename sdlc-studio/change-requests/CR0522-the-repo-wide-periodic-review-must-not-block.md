# CR-0522: the repo-wide periodic review must not block a sprint close whose own work is fully reviewed

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Date:** 2026-08-01
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** 2026-08-01T08:00:52Z

## Summary

`sprint close` gates on the `review-current` lane, which measures staleness of the REPO-WIDE five-leg unified review (`reviews/LATEST.md`). That review covers all ~1862 artefacts and runs on its own cadence. It has nothing to do with whether the sprint being closed was reviewed.

Measured on RUN-01KYY52D: nine units, each carrying independent adversarial evidence, an APPROVE verdict recorded after its findings were repaired, a confirmation pass over the repairs, and a reviewer-of-record sign-off. Both suites green. The close outstanding set went 19 -> 1, and the ONE remaining item is that the unified review is 59 artefacts stale - staleness that pre-dates the run and that the run did nothing to cause.

`--file-and-close`, the documented bounded exit for a blocked close, refuses it too: it classifies `review-current` as a hard correctness blocker and 'a correctness gate is never filed away'. That classification is the defect. A stale PERIODIC review is a cadence fact, not a correctness fact about this batch - nothing about the code is unproven, and the sprint's own review coverage lane passes.

So a fully reviewed, fully signed-off sprint cannot close by any route, and the only ways out are to run an unrelated repo-wide ceremony or to leave the run open indefinitely.

## Impact

Every sprint close inherits the deferral history of a ceremony it does not own. Because a sprint is nearly always in flight, the coupling also makes the unified review MORE likely to be deferred, not less: the pressure to close a sprint becomes pressure to rush or skip the repo review, which is the opposite of the intent. It also blocks unattended and scheduled runs, and it interacts badly with CR0514 - a panel that can sign off still cannot close.

## Acceptance Criteria

- [ ] A sprint whose own units all carry independent review coverage and sign-off can close while the repo-wide unified review is stale.
- [ ] The staleness is REPORTED at close - in the close output, the retro and the close-owed ledger - never silently dropped.
- [ ] `--file-and-close` accepts a stale periodic review as ceremony debt and files it as a real artefact linked to the run.
- [ ] A sprint whose own review coverage is INCOMPLETE still blocks - the positive control, so this does not become a way to close an unreviewed batch.
- [ ] If a threshold is adopted, it is declared in config and the close states which side of it the current staleness falls on.
- [ ] A test pins that a fully-covered batch closes with a stale unified review, and that an uncovered one still refuses - the mutant is a change that makes both pass.

## Recommendation

Decouple the two. `sprint close` should gate on THIS sprint's review coverage, which it already checks and which passed here. Reclassify `review-current` for the close as a cadence WARNING that is reported loudly, named in the retro and carried in the close-owed ledger - not a hard blocker.

If the cadence still needs teeth, put them on a threshold rather than on any staleness at all: warn below a declared limit, block above it, so the ceremony is enforced without every sprint paying for the last one's deferral. Either way `--file-and-close` must be able to file it, because a periodic review being overdue is exactly the ceremony debt that exit exists to name.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | Claude Opus 5 | Raised |
