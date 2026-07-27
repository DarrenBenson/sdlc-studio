# EP0177: Make the discipline cheaper than the sloppiness it replaces: run the tests the change can reach, at the boundaries that matter

> **Status:** Draft
> **Parent:** CR0455
> **Parent:** CR0452
> **Parent:** CR0450
> **Parent:** CR0454
> **Parent:** CR0453
> **Derived Point Total:** 60
> **Parent:** CR0451
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0451. Delivers the work CR0451 requested.

## Story Breakdown

- [ ] [US0493: The test-relevant surface is hashed, and a run whose surface is unchanged since the last green verdict is skipped with that verdict reused](../stories/US0493-the-test-relevant-surface-is-hashed-and-a.md)
- [ ] [US0494: The gate selects the tests a change can reach from the import graph, reporting what it excluded and falling back to everything when it cannot resolve](../stories/US0494-the-gate-selects-the-tests-a-change-can.md)
- [ ] [US0495: A full-suite run happens only at a boundary - push, release and sprint close - and the policy is stated where an operator reads it](../stories/US0495-a-full-suite-run-happens-only-at-a.md)
- [ ] [US0496: The gate reports its own cost per run against a budget, so a regression in gate time is as visible as a regression in behaviour](../stories/US0496-the-gate-reports-its-own-cost-per-run.md)
- [ ] [US0497: The plan-time test strategy states the execution policy - what runs per commit, at close and at release, with its estimated cost](../stories/US0497-the-plan-time-test-strategy-states-the-execution.md)
- [ ] [US0498: The test strategy is persisted with the plan and read back at close, so it can be reviewed, signed off and compared with what ran](../stories/US0498-the-test-strategy-is-persisted-with-the-plan.md)
- [ ] [US0499: The close reports execution actuals against the declared policy, so a sprint that ran the suite fifty times shows it](../stories/US0499-the-close-reports-execution-actuals-against-the-declared.md)
- [ ] [US0500: An artefact the close itself creates does not count as an unreviewed change against that same close](../stories/US0500-an-artefact-the-close-itself-creates-does-not.md)
- [ ] [US0501: A close retry over an unchanged test-relevant surface reuses the previous gate verdict instead of re-running it](../stories/US0501-a-close-retry-over-an-unchanged-test-relevant.md)
- [ ] [US0502: The doctrine names the silent-stall failure mode and gives a driving agent a detection rule it can apply](../stories/US0502-the-doctrine-names-the-silent-stall-failure-mode.md)
- [ ] [US0503: A delegated task that stops without a result is reported as unfinished, never as pending, and the audit quorum rule cross-references it](../stories/US0503-a-delegated-task-that-stops-without-a-result.md)
- [ ] [US0504: Mutation testing by a delegated reviewer runs in an isolated checkout, and mutation.py refuses to mutate a file with uncommitted changes](../stories/US0504-mutation-testing-by-a-delegated-reviewer-runs-in.md)
- [ ] [US0505: A repair that changes behaviour carries a test asserting that behaviour, so a later silent revert reddens the suite](../stories/US0505-a-repair-that-changes-behaviour-carries-a-test.md)
- [ ] [US0506: A report attributes suite time and test count to the module each test covers, so the expensive areas are visible](../stories/US0506-a-report-attributes-suite-time-and-test-count.md)
- [ ] [US0507: A test no mutation of its own module can kill is reported as a removal candidate, and removing one records what it no longer protects](../stories/US0507-a-test-no-mutation-of-its-own-module.md)

## Acceptance Criteria (Epic Level)

- [ ] A full-suite run happens only at a BOUNDARY - push, release, and sprint close - never per commit. Everywhere else the gate runs what the change can reach.
- [ ] The suite is skipped entirely when the test-relevant surface is unchanged since the last green run, judged by a content hash of that surface rather than per-commit file types, so consecutive paperwork commits and a re-run of a close pay nothing.
- [ ] Test selection is by changed surface rather than binary: a commit runs the tests reachable from the files it touches, derived from the import graph the repo map already builds, not the whole suite.
- [ ] The safety net is stated and enforced: the full suite still runs somewhere it cannot be skipped - a push or release lane - so selection trades per-commit latency for a later full run, never for less coverage.
- [ ] A selected run reports what it EXCLUDED and why, so a developer can see the gate made a judgement rather than silently testing less; a file whose dependents cannot be resolved falls back to running everything, never to running nothing.
- [ ] The gate's own cost is measured and reported against a budget per commit, so a regression in gate time is visible in the same way a regression in behaviour is.
- [ ] Review drives mutation through `mutation.py` rather than an agent generating mutants one subprocess at a time, and the delivery path ships a differential harness that replays a fixed defect against the pre-fix commit.

### From CR0453

- [ ] The plan-time test strategy states the EXECUTION policy as well as the proof obligations: what runs per commit, what runs at close, what runs at release, and the estimated cost of each.
- [ ] The strategy is persisted with the plan rather than printed only, so it can be reviewed at plan time, signed off with the goal, and read back afterwards.
- [ ] The close reports execution actuals against that policy - how many full-suite runs happened and what they cost - so a sprint that ran the suite fifty times shows it in the retro rather than hiding it.
- [ ] A strategy whose declared per-commit policy differs from what the hook actually does is reported, so the two cannot silently disagree about the most expensive decision in the sprint.

### From CR0454

- [ ] An artefact created BY the close - the anchor, the handoff, a finding filed during it - does not count as an unreviewed change against that same close.
- [ ] The close's gate runs once for a given tree state; a retry over an unchanged test-relevant surface reuses the previous verdict rather than re-running it.
- [ ] When the close does refuse, it distinguishes a blocker in the WORK from a blocker it created itself, and names which.

### From CR0450

- [ ] The doctrine names the silent-stall failure mode: a delegated agent can stop without erroring, and an absent result must never be read as a pending one.
- [ ] It gives a concrete detection rule a driving agent can apply - the delegate's transcript size and modification time distinguish thinking from dead, and the presence of a result marker says whether it finished - rather than instructing the driver to wait for a signal that a dead delegate never sends.
- [ ] It states the preference for a structured-output delegation over free-form completion for long or wide tasks, with the evidence recorded and the causal claim explicitly hedged, so a reader can re-judge it if the harness behaviour changes.
- [ ] The audit reference cross-references its own dead-vote quorum rule to this one, so the two halves of the same class - an absent vote and an absent agent - are read together rather than discovered separately.

### From CR0452

- [ ] The doctrine states that mutation testing by a delegated reviewer runs in an isolated checkout - a worktree or a copy - never in the tree the author is working from, and says why.
- [ ] It states the author-side rule that follows: do not stage with a whole-tree add while delegated agents are running, because their working state is indistinguishable from your own.
- [ ] `mutation.py` refuses, or loudly warns, when asked to mutate a file with uncommitted changes or inside a checkout that is not its own, so the safe path is the default rather than a thing to remember.
- [ ] A repair that changes behaviour carries a test asserting that behaviour, so a later silent revert reddens the suite instead of passing it - three repairs in this sprint shipped unpinned and one of them was reverted.

### From CR0455

- [ ] A report attributes suite time and test count to the module each test covers, so the expensive areas are visible rather than guessed.
- [ ] A recurring review asks of each area whether its tests still discriminate - a test that no mutation of its own module can kill is a candidate for removal, not just a slow one.
- [ ] Removing a test requires the same evidence as adding one: a statement of what it no longer protects, recorded, so pruning cannot quietly become coverage loss.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
