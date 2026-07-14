# RFC-0037: Backlog triage as a first-class ceremony: keep the backlog clean and actionable BEFORE planning

> **Status:** Draft
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/status.py
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

CR0260 made the unit-level question unavoidable - is THIS ITEM plannable (does it declare Affects and a size)? The BACKLOG-level question has no home at all: is this backlog COHERENT? In real teams that is grooming or triage, and it runs BEFORE planning precisely so the plan is not built on a dirty backlog. Operator raised it, and one days dogfooding proves it.

What fell out of ONE planning session, all caught by a human looking rather than by tooling:

- THREE duplicate pairs in a backlog of eleven. BG0139 was entirely subsumed by CR0262 - the same fix filed twice, hours apart, by the same agent. CR0261 and CR0263 were structurally identical. BG0137 and BG0138 both fixed the same file. They surfaced only because CR0260 shared-file clustering happened to put them in one collision cluster.
- TWO bugs with no Affects, filed in the window before the filer could record the field.
- One unit that should have been DECOMPOSED rather than sized.

Breakdown and triage are different ceremonies. Breakdown asks whether a unit can be planned. Triage asks whether the backlog is worth planning FROM: are these items distinct, current, correctly sized, correctly ordered, and still wanted?

A sharp constraint from the estimation literature belongs here too: estimator consistency COLLAPSES above about 5 points - people cannot reliably size anything more than about five times a reference unit. So "this unit is too big to size" is not an estimation failure, it is a TRIAGE failure, and the answer is to split it. Triage is where that decision belongs.

The design constraint is LL0027: a gate belongs in the command people actually run. A triage step that is a separate command WILL NOT BE RUN - this project has proved that three times (the design rung nobody invoked, the retro gate satisfiable by touch, the advisory review that let a stale one through). So triage must live inside `plan`, as breakdown does. What is genuinely open is which lenses BLOCK and which merely REPORT, because a duplicate is a judgement call in a way a missing Affects is not.

This RFC absorbs CR0264 (duplicate detection at filing), which is one lens of the same ceremony.

## Design Options

- **Triage inside `plan` (RECOMMENDED). Add a triage pass alongside the breakdown gate. Duplicates, superseded items, oversized units and stale artefacts are surfaced in the plan the operator already reads. Blocking for the mechanical lenses (an oversized unit must be decomposed), reporting for the judgement ones (a suspected duplicate names its candidate; the human decides). Consistent with LL0027 - the command people actually run.**
- **A separate `triage` command, run before plan. Cleaner separation, and a real backlog-grooming session has a natural home. But this project has now proved three times that an optional ceremony is not performed. It would need `plan` to REFUSE a backlog that has not been triaged since it last changed - at which point the separation buys nothing and costs a second command.**
- **Detection at FILING only (CR0264 alone). Catch a duplicate when it is created, which is the cheapest moment and the one where the author has the most context. Necessary but not sufficient: it does nothing for staleness, mis-ordering, or a unit that became a duplicate because something ELSE was filed later.**

## Recommendation

Triage inside `plan`, with filing-time duplicate detection (CR0264) as its cheapest lens. The lenses worth having, in rough order of value: DUPLICATE/SUBSUMED (name the candidate, do not auto-refuse); OVERSIZED (block - a unit above roughly 5 points cannot be sized reliably by anyone, so decompose it); SUPERSEDED (an artefact whose work another has absorbed); STALE (open, untouched for months, nothing depends on it - ask whether it is still wanted); ORPHANED DEPENDENCY (depends on something terminal). State plainly which lenses block and which report, and log what a lens dropped, so a silent truncation never reads as clean.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Act on this finding or keep status quo | Open |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |
