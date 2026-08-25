# CR-0555: The expensive half of the test-plan gate fires before a diff exists, so move it to where one does instead of banding a signal that cannot discriminate

> **Status:** In Progress
> **Decomposed-into:** EP0218
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/reference-config.md
> **Evidence:** RUN-01M0JD1W, 2026-08-24: five plan-review rounds on three units, and the gate refused BG0606 - a bug whose fix had already shipped and been independently approved. CR0549's three failed remedies are recorded in that CR's corrections; D0150 rules out the class the third one belonged to.
> **Date:** 2026-08-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_test_plan_gate` demands two different things at entry to implementation: that a `## Test Plan` EXISTS, and that an independent seat has APPROVED it. The first is cheap and is the falsifiability rule this project is built on. The second is the expensive one - it cost five plan-review rounds on three units in RUN-01M0JD1W - and it is the reason 20 of 21 open bugs cannot reach Fixed. CR0549 tried to make it proportional by banding risk, and failed three specifications for one structural reason: the gate fires BEFORE the unit is implemented, so the only signals available are the author's own declarations, and D0150 now forbids those from gating review depth. The gate does not need to be banded. It needs to fire later. `critic.tier_for` already reads a post-code band successfully, because by then a diff exists.

## Impact

Every project using the skill. Today a two-line bug fix and a rewrite pay the identical pre-code ceremony, and the ceremony is paid before anyone can see what the change is. BG0606 is the concrete case: its fix shipped and was independently approved, and it is still Open because closing it needs a plan review for work already reviewed. Nothing changes for the authoring rule - a criterion must still name a production change its test dies on, at every band - so this narrows WHEN the independent approval is demanded, not WHETHER a plan is required.

## Scope note, 2026-08-25: this request MOVES the gate and does not scope it

An earlier draft of AC4 had the terminal gate read a diff-basis band. That is deliberately out of
scope here. CR0549's remedy failed three specifications on banding, and D0150 rules out the whole
pre-code family; adding a band to this request would re-import the risk that killed it.

**What the move alone buys, without any band.** The plan review and the delivery review currently
bind at opposite ends of a unit's life, so a unit pays two independent review cycles. Bound at the
same point they are one brief and one round - and the reviewer can see the CODE while judging the
plan, which is the thing that took five rounds to establish by hand on RUN-01M0JD1W: whether a
declared mutant can actually fail the test its criterion names is a question about the diff, and
the pre-code reviewer cannot answer it.

**Scoping by band remains open** and is worth doing once a signal exists that D0150 permits - one
derived from the change rather than declared by its author. It belongs in its own request, argued
on its own measurement, and it should not be bundled here.

## Correction, 2026-08-25: the saving this request claims does not exist for BUGS

A pre-code goal review rejected the batch refined from this request, and its first finding
invalidates the premise. Verified in the source rather than relayed: `transition.py:961` reads

```python
if type_ == "story" and not force and target_canon == "Done":
```

so the two-role delivery review is STORY-only and DONE-only. A bug reaching `Fixed` passes
`_bug_depth_gate`, which asks for a parseable `Verification depth` and is not a review, and passes
no independent delivery review at all.

**So for the 20 of 21 open bugs this request leads with, there is NO gated independent review at
all.** The
"two cycles become one round" saving holds only for stories reaching Done. BG0606, the evidence
case named in this request's own Impact section, stays blocked after the move: it still owes a
plan, and it still owes an independent approval, now demanded at `Fixed` instead of at entry.

**What the finding exposes is more interesting than the request it kills.** Bugs pay an
independent review BEFORE the code exists and none after. The expensive judgement is spent on a
test plan nobody can check against an implementation, and the implementation itself is never
independently reviewed at all. Whether that is the right way round is the question this request
should have asked first, and did not.

This request is NOT withdrawn - the move may still be right for stories - but its claim must be
narrowed to stories and re-argued, and the bug population needs a different answer.

## Second correction, 2026-08-25: bugs owe no independent review, and this request never applied to them

The correction above was itself wrong one layer down, and D0151 - recorded hours earlier - exists
to stop exactly this. Measured through the shipped entry point across all 23 open bugs rather than
read: NOT ONE owes an independent review of any kind.

For a bug, `Fixed` is not in `_IMPL_TARGETS`, so the entry `_test_plan_gate` NEVER FIRES. The
demand a bug meets is `_planned_mutant_gate` at the terminal transition (`transition.py:921`,
message at `:1922`), which requires a `## Test Plan` whose planned mutants have been executed - and
contains no verdict check, no `APPROVE`, no independence test. Two different functions carry the
identical "has no `## Test Plan`" message, and the bug refusal was attributed to the wrong one.

What the 23 open bugs actually owe, by dry-run: 21 a test plan, 20 a `Verification depth`, 18
ticked criteria carrying `Verify:` lines, 1 its mutants executed, and 1 nothing at all. Every one
of those is mechanical and self-service. The five-round ceremony that made RUN-01M0JD1W expensive
is a STORY cost.

**This request therefore never applied to bugs**, and its Impact section leading with them was
wrong from the moment it was filed. It is narrowed to stories, where the two-cycle saving is real.
The bug population needs no relief from this gate; whether it needs MORE review is a separate
question, and the honest observation is that a bug today gets no independent judgement of either
its plan or its code.

## Acceptance Criteria

- [ ] Given a unit entering implementation, when the gate runs, then a `## Test Plan` is still REQUIRED and its absence still refuses - the authoring-time rule is untouched at every band
- [ ] Given that same unit entering implementation, when the gate runs, then an independent plan-review approval is NOT demanded there, and the refusal message says when it will be
- [ ] Given a unit reaching a terminal status, when the gate runs, then the independent plan-review approval IS demanded, and a unit without one is refused exactly as it is refused at entry today
- [ ] Given the plan review and the delivery review now binding at the SAME point, when a reviewer is briefed, then both are carried in one brief, so a unit takes one round where it took two - this is the saving the move buys, and it needs no band at all
- [ ] Given a project that has not adopted this, when it transitions a unit, then behaviour is unchanged - the move is behind the same dated cutoff the existing gate uses, so an existing backlog is not retro-refused
- [ ] Given the close, when it reports, then it names units whose plan approval was demanded at terminal and those exempted by the cutoff, so the move is visible rather than silent

## Recommendation

Option 1. The plan must still EXIST at entry, which preserves the authoring-time rule and costs nothing; only the independent approval moves. At the terminal transition a diff resolves, so the band is measured from the change - which is what D0150 requires and what `critic.tier_for` already does. The two-role delivery review and the plan review then both bind at the same point and can be briefed together, which is also the cheaper shape.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-24 | sdlc-studio | Raised |
| 2026-08-25 | sdlc-studio | Scope note: AC4 re-cut from a diff-basis band to the one-brief saving. Banding is deferred to its own request - three specifications died on it. |
| 2026-08-25 | sdlc-studio | Correction: the two-role gate is story-and-Done only (transition.py:961), so the saving does not exist for bugs and BG0606 stays blocked. Claim must narrow to stories. |
| 2026-08-25 | sdlc-studio | Second correction: measured across all 23 open bugs - NONE owes an independent review. The entry gate never fires for a bug. Request narrowed to stories; its bug Impact was wrong as filed. |
