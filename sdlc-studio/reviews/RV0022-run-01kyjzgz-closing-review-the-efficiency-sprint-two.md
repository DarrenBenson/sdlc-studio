# RV-0022: RUN-01KYJZGZ closing review: the efficiency sprint, two REJECT rounds

> **Date:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1

## Scope

RUN-01KYJZGZ: 33 units, 107 points - EP0177's fifteen efficiency stories plus eighteen bugs chosen
for file-disjointness so they could run as parallel lanes beside the sequential gate work. Diff base
14eb4447..HEAD, delivery at b086e869 with repairs at cceb6808 and after.

Sprint Goal: the cost of running the discipline falls below the cost of the work it guards - the
suite runs only when the code it tests has changed, and only in full where a wrong answer is
expensive.

Reviewed independently in two rounds by five reviewers over disjoint slices, none of whom wrote any
of it, plus the operator as reviewer of record.

## Deterministic evidence

- Skill suite 4,755 and tools suite 426: both green. Drift zero. Installed copy in sync.
- Selection measured on a real change: a change to one script selects 62 of 157 test modules.
- The surface hashes 2,517 tracked files in 0.04s.
- Four delivery lanes and one review slice died mid-run and were re-run; twenty units were unreviewed
  until a second pass was commissioned for them alone.

## Findings

**Round one: REJECT, 9 major.** The efficiency core was wired to nothing that runs tests - the
selection was computed by one hook and ignored by the one that executes suites, and no production
path recorded a verdict, so the skip branch was unreachable however well it tested. The skip fired
over a change the tests catch, because the surface covered only the files the suites were MEASURED
to read and omitted 233 tracked files; editing SKILL.md left the digest byte-identical while three
tests went red. Selection claimed itself resolved while missing real dependents, because 57 of 162
modules measure an empty read set and silence was counted as reaching nothing. A boundary could
reuse a verdict, inheriting every gap in whatever produced it.

**Round two: REJECT, 11 major**, including twenty units that had had no independent look at all.
BG0312's repair inverted the harm it was filed for: a repo carrying nothing but an installed copy of
this skill classified brownfield, and the unit's own AC3 asserts the opposite property while its
verifier exercised only the cases that do not bite. Six units reached Fixed with no acceptance
criteria and no verifier, four with no delivery row, while real code landed against each. US0507
shipped a consumer whose evidence no producer emits.

**Repair.** All twenty are closed. The surface is every tracked file and an unenumerable tree is
unanswerable rather than a stable digest of nothing. Unattributable modules are always included. A
boundary always runs full. The selection travels through the handover and the hook that runs tests
consumes it and records the green. The classifier prunes agent-tooling directories, pinned in both
directions. The six units carry authored criteria. US0507's scope is stated on the artefact.

**Residuals filed rather than absorbed:** BG0351 (the constitution lane is 81% of the artefact gate),
BG0352, BG0353, BG0354, BG0355 (a lane can die leaving finished work unrecorded), BG0356, BG0357
(the mutation producer half), CR0456, CR0457, CR0458, CR0459 (a bug can reach Fixed with no criteria).

## Verdict

**Goal PARTIAL, work approved for sign-off.**

The mechanisms are built, correct and pinned. The goal was that the cost falls, and that is not yet
demonstrated in production: no commit has been measured end to end under the new wiring. Recording
this as achieved would be the same false claim the reviewers refused twice.

The honest summary is that this sprint's delivery was not trustworthy and its review was, for the
second time running. The same defect class appeared four times - a correct mechanism reaching no
caller - and every instance was invisible to a green suite, to the gate, and to the author. Three of
the four were caught by readers who did not write the code; the fourth was caught by a delivery
lane's own friction report, which is the strongest argument for the standing instruction to raise
friction rather than work around it.

Signed off by Darren Benson as reviewer of record.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
