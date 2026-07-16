# RFC-0037: Backlog triage as a first-class ceremony: keep the backlog clean and actionable BEFORE planning

> **Status:** Accepted
> **Decomposed-into:** EP0047
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

## How triage state is recorded (operator proposal, 2026-07-14)

Operator: *"Maybe we should flag a groomed or triaged item from one that is not - or at least a date of
last triage?"* The second half is the right answer, and the first half is a trap worth naming.

### GROOMED is derived - never stamp it

`sprint.breakdown()` already computes it from the artefact itself: does it declare `Affects`, does it
declare a size. **Derived state cannot lie and cannot go stale.** A `Groomed: yes` stamp creates a fact
that can be true in the stamp and false in the file, and under a gate somebody will set it to get past
the gate. Keep it computed. There is nothing to record.

### TRIAGED is a judgement - record it, but NOT as a boolean

Triage is a human decision ("I looked: this is not a duplicate, it is still wanted, it is sized right").
Nothing can derive it, so it has to be written down. But `Triaged: yes` is precisely the failure this
project already has a lesson for - **L-0008: a gate that checks an artefact EXISTS, not what is IN it,
is satisfied by `touch`.** The retro gate died of exactly this: an empty file with the right name passed
it. A triage boolean is the same artefact in a new costume, and under a gate it becomes a reflex.

### Record the DATE, and derive staleness from the backlog moving underneath it

**A triage decision is a judgement made against a backlog SNAPSHOT, and it decays when the backlog
changes.** "This is not a duplicate" was true when it was checked, and says NOTHING about the artefact
filed an hour later. So triage does not go stale after thirty days. It goes stale **the moment something
is filed that could invalidate it.**

Two precedents in this repo already implement exactly this shape:

- **`review-current` (CR0253):** `reviews/LATEST.md` must be at least as new as EVERY artefact; if any
  changed since, the review is stale and the close is refused. The machinery (`review_prep.staleness`,
  git commit time with an mtime fallback) is reusable as-is.
- **Lessons validity:** every lesson carries a `Review-by` horizon and `lessons revalidate` forces a
  decision - closed, extended, or still within its horizon.

### The rule

> `> **Triaged:** 2026-07-14` on the artefact. A unit's triage is STALE if any artefact was CREATED
> after that date (a new candidate for duplication that the triage never saw), or if the unit itself
> changed after it. `sprint plan` reports stale triage alongside the shared-file clusters.

Conservative on purpose: a newly filed artefact could duplicate almost anything, so any new filing
staleness-marks the untriaged judgement rather than pretending to reason about which pairs are at risk.
That is the same conservatism the review gate already applies, and it is why the review gate has now
caught its own sprint twice.

**And it degrades honestly.** An artefact with no `Triaged:` line has never been triaged - which is a
FACT, not a failure, and is exactly what a fresh backlog looks like. It reports; it does not block. The
blocking lens stays the mechanical one (an oversized unit must be decomposed), because a duplicate is a
judgement and only the author can settle it.
