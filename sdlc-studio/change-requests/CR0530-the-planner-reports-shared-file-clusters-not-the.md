# CR-0530: the planner reports shared-file clusters, not the parallelisable fraction, so nothing says whether agentic delivery is available at all

> **Status:** In Progress
> **Decomposed-into:** EP0230
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md
> **Date:** 2026-08-04
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`--agentic` has shipped since v3 and its safety rule is exact: stories in a wave must modify zero files in common, and it falls back to sequential when they do. Deciding whether to use it therefore needs one number - how much of a batch is actually disjoint - and nothing computes it.

`sprint breakdown` reports SHARED-FILE CLUSTERS, which is a different measure and misleads in the direction that matters. Over the 42 open Ready/Open units it reports `2 shared-file clusters`. The connected-component structure over the same Affects graph is 6 components, and ONE of them holds 36 units and 145 of the 163 points - 88 percent of the remaining work, strictly serial. A planner reading `2 clusters` cannot tell that one cluster is almost the whole backlog; the phrasing suggests two comparable halves.

The wave analysis itself also has no command. `reference-epic.md` documents it as four judgement steps over layer tables and hub-file tables, executed by reading. Answering it for EP0176 required hand-rolling a union-find over the Affects graph in a throwaway script - which AGENTS.md names as a finding to file rather than something to repeat.

## A file-disjoint unit is not necessarily an independent one

Found while trying to deliver the one unit this analysis called parallelisable. US0492 documents
the queue lifecycle and its `Affects` names only `help/sprint.md` and `reference-sprint.md`, so
it shares no file with anything and every seam check calls it free. It is not: its AC1 asserts
that every queue verb THE PARSER DEFINES is documented, and the parser defines none until
US0488 to US0491 build them. Delivered first, the criterion passes over an empty set - the
vacuous-verifier shape, arrived at through a scheduling decision rather than a badly written
test.

So the component count this request asks for is necessary and not sufficient. It answers "can
these two edit the same file at once", which is the question `--agentic`'s safety rule asks, and
`reference-epic.md` already knows the rest is judgement - its wave table marks cross-layer pairs
CAUTION rather than SAFE for exactly this reason ("page may need types from this backend
story"). The number should therefore be reported as what it is: an upper bound on parallelism,
not a schedule. A unit whose criteria READ a surface another unit CREATES is coupled however
disjoint its Affects.

## Impact

Two costs. An operator cannot tell whether `--agentic` is worth invoking without doing the analysis by hand, so the flag is either used blindly or not used at all. And a planner reading `2 shared-file clusters` over a backlog that is 88 percent one serial component is being given a number that is true and misleading at once - the shape of the batch is concentrated where the report suggests it is split.

## Acceptance Criteria

- [ ] `sprint breakdown` reports the number of INDEPENDENT components over the batch's declared Affects graph, not only the shared-file clusters, so a batch that is one serial mass and a batch that is several parallel lanes read differently.
- [ ] It reports the concentration, not just the count: the size of the largest component in units and points, and that as a share of the batch. Over today's 42 open units the answer is 36 units and 145 of 163 points, 88 percent, and no current output says so.
- [ ] The two measures are distinguished in the wording, because they are both true and answer different questions - a file-shared cluster says which units collide, a component says how many lanes exist. Reporting one under the other's name is what made `2 clusters` read as two comparable halves.
- [ ] A runbook row names the command, so the question `is this batch parallelisable` has a command behind it rather than four judgement steps read out of a reference file and executed by hand.
- [ ] The `--agentic` safety rule is UNCHANGED and is not made the default. The measurement that motivated this showed the flag would correctly decline 88 percent of the current backlog, which is the guarantee holding rather than a gap.

## Recommendation

Have `sprint breakdown` compute connected components over the declared Affects graph and report the parallelisable fraction beside the cluster list: how many independent lanes exist, how many points sit in the largest, and what percentage of the batch that is. The union-find is a dozen lines and the data is already loaded. Then add a runbook row so the question has a command behind it. Explicitly NOT proposed: making `--agentic` the default, or changing its safety rule. The measurement showed it would correctly decline 88 percent of this backlog, which is the flag working, not failing.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-04 | sdlc-studio | Raised |
