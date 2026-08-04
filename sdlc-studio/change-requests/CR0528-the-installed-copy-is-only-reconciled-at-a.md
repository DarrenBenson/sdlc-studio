# CR-0528: the installed copy is only reconciled at a close, so a fix believed shipped is in force nowhere for the length of a run

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** tools/forward-port.sh, .githooks/pre-push, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Date:** 2026-08-04
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`sprint close` blocks on the `installed-copy` preflight lane - it refused RUN-01KZ56M6's close with `14 file(s) differ ... the work this close is signing off is in force nowhere else`, and the mirror ran. That gate is real and it works. What it does not cover is the WINDOW: nothing between two closes asks whether the installed copy has drifted, so every commit from the first of a run to its close lands in this repository and in no consuming project. RUN-01KZ56M6 spanned nine delivery commits before the mirror caught up. AGENTS.md already names the hazard in terms - `the installed copy is what every other project on this machine loads, so the window between a fix landing here and the mirror running is a window in which a fix believed shipped is in force nowhere` - and then leaves the window open for the length of a run. The programme now underway makes that materially worse: the operator has re-planned it as more, smaller runs, and a longer sequence of runs is a longer sequence of windows.

This is a POLICY question, not a defect, which is why it is filed rather than fixed. Mirroring on every commit is the obvious answer and is probably wrong: the mirror is a sweep over the whole skill tree, a commit is not a reviewed unit, and pushing unreviewed work into the copy every project loads is the failure the never-run-install-from-the-dev-repo rule exists to prevent. Mirroring at PUSH is the candidate worth pricing - a push is the point at which work leaves this machine's working set and becomes something another session can pull.

## Impact

A consuming project can load a skill that is one whole run behind the repository, with no signal that it is. The failure is silent in the direction that matters: the fix exists, its tests pass, its paperwork says shipped, and the project that needed it does not have it. Nobody looks, because the close will eventually reconcile and the drift never appears in a report.

## Acceptance Criteria

- [ ] The drift between this repository's skill source and the installed copy is reported at a point BEFORE the close - the chosen point being priced by this request, with push as the candidate - so a fix cannot sit in force nowhere for the length of a run.
- [ ] The report names the drifted files, not a count: `forward-port --check` already does, and a signal that says only 'something differs' sends the reader to run the sweep to find out, which is the cost the check exists to avoid.
- [ ] The two states `forward-port --check` already reports rather than fails - no installed copy, and a copy holding a `.local/forward-port.pin` marker - stay reported rather than failed at the new point too, or a machine that deliberately does not mirror starts refusing work it has no stake in.
- [ ] The `sprint close` installed-copy gate is UNCHANGED and still blocks. Whatever is added earlier is a narrowing of the window, never a replacement for the backstop that has already proven it fires.
- [ ] Which shape was chosen - refuse, warn, or mirror - is recorded as a decision with its reasoning, because a warning nobody reads and a refusal everybody disables are different failures and the record must say which one was accepted.

## Recommendation

Price a pre-push drift check first, since push is where work becomes visible to another session, and decide between three shapes: (a) pre-push REFUSES on drift, which is strongest and also the most likely to be switched off, since a mirror sweep on every push is a real cost; (b) pre-push WARNS and names the drifted files, which costs nothing and relies on somebody reading it - the weak shape AGENTS.md warns about; (c) pre-push mirrors automatically, which is fastest to use and quietly widens what an unreviewed commit can reach. Whichever is chosen, the close gate stays: it is the backstop and it has already proven it fires.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-04 | sdlc-studio | Raised |
