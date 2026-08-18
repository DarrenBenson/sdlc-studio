# SC0006: v5 runs 5 to 7: the open bug backlog reaches zero, in file-disjoint clusters

> **Status:** Spent
> **Queue rank:** 5
> **Created:** 2026-08-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Appetite:** 480min/8units
> **Scope query:** --bugs Open

## Sprint Goal

Zero open bugs. Every remaining finding is either fixed and verified, or closed with a recorded ruling that says why it is not a defect.

## Scope rule

Every bug still Open after runs 1 to 4 - roughly 32 Medium plus the residual High, re-forecast
from run 4's grooming result.

This is written as one charter covering three runs because the split between them cannot be
decided today: it depends on run 4's re-estimate and on which units can run in parallel.
`sprint breakdown` currently reports ONE shared-file cluster containing almost the entire
backlog - `close_owed.py`, critic.py, gate.py and 25 more - so the parallel-worktree pattern that
paid off on the audit-backlog sprint is largely unavailable here, and these runs should be
planned as sequential file-disjoint groups rather than as concurrent subagents.

Two classes inside it want different handling. The mutation-evidence family (BG0550 to BG0554,
BG0531) is only reachable by a project that has turned mutation evidence on, and BG0552 is the
one to read first - a cross-provenance contradiction is currently undetectable, which is the
case the whole rule turns on. The close-ceremony family (BG0540, BG0544, BG0547, BG0549, BG0469,
BG0509, BG0512, BG0526) is reachable by any project that runs a sprint to its close, so it
carries the higher consumer weight despite the lower severity.

A finding ruled not-a-defect is closed with that ruling recorded on the artefact. The decision
was zero OPEN, not zero filed.

## Seat review

_Not yet reviewed._

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-09 | sdlc-studio | Created via `new` (deterministic) |
