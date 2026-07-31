# HO-0038: No gate reports green over something it did not check, and the standing review debt goes to zero HONESTLY: every unit at Review carries an independent recorded verdict, every rejection carries a filed finding with an executed reproduction, and every gate this batch touches either checks what it claims or states plainly that it did not

> **Date:** 2026-07-31
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KYTKA1 (started 2026-07-30T22:50:38Z)
> **Outcome:** stopped
> **Goal:** done
> **Batch source:** run-state.json

## Where to pick up

Every unit in the batch is terminal. There is no tail: close the run and plan the next batch normally.

## Appetite

- **Declared:** wall-clock 600 min, units 46 unit(s)
- **Spent:** 624.6 min, 20 unit(s) terminal
- **Delivered:** 20 unit(s)
- **Token forecast:** ~3,273,537 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (20)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0442](../../sdlc-studio/bugs/BG0442-the-close-s-finding-placement-metric-is-hardcoded.md) | bug | Fixed | 3/3 AC(s) verified; critic APPROVE (engineering seat (independent, isolated worktree, rejoinder over the repair)) |
| [BG0443](../../sdlc-studio/bugs/BG0443-critic-is-independent-returns-true-when-no-reviewer.md) | bug | Fixed | 3/3 AC(s) verified; critic APPROVE (engineering seat (independent, isolated worktree, closing full-diff review)) |
| [BG0444](../../sdlc-studio/bugs/BG0444-the-pre-gate-independence-hole-was-closed-in.md) | bug | Fixed | 3/3 AC(s) verified; critic APPROVE (engineering seat (independent, isolated worktree, closing full-diff review)) |
| [BG0447](../../sdlc-studio/bugs/BG0447-the-availability-guard-tests-for-gh-as-a.md) | bug | Fixed | 2/2 AC(s) verified; critic APPROVE (engineering seat (independent, isolated worktree, closing full-diff review)) |
| [BG0439](../../sdlc-studio/bugs/BG0439-the-dead-flags-hook-lane-tells-the-operator.md) | bug | Fixed | 1/1 AC(s) verified; critic APPROVE (engineering seat (independent, isolated worktree, closing full-diff review)) |
| [BG0417](../../sdlc-studio/bugs/BG0417-transition-done-never-checks-the-two-role-rule.md) | bug | Fixed | 4/4 AC(s) verified; critic APPROVE (engineering seat (independent, isolated worktree, closing full-diff review)) |
| [BG0429](../../sdlc-studio/bugs/BG0429-the-dead-flag-detector-collapses-same-named-functions.md) | bug | Fixed | 3/3 AC(s) verified; critic APPROVE (engineering seat (independent, isolated worktree, closing full-diff review)) |
| [BG0440](../../sdlc-studio/bugs/BG0440-the-isolated-checkout-rule-is-enforced-author-side.md) | bug | Fixed | 4/4 AC(s) verified; critic APPROVE (engineering seat (independent, isolated worktree, closing full-diff review)) |
| [BG0449](../../sdlc-studio/bugs/BG0449-the-plan-s-grooming-gate-reported-ok-in.md) | bug | Fixed | 4/4 AC(s) verified; critic APPROVE (engineering seat (independent, isolated worktree, closing full-diff review)) |
| [BG0452](../../sdlc-studio/bugs/BG0452-verifiers-all-green-splits-the-artefact-key-on.md) | bug | Fixed | 3/3 AC(s) verified; critic APPROVE (engineering seat (independent, isolated worktree, rejoinder over the repair)) |
| [BG0430](../../sdlc-studio/bugs/BG0430-a-namespace-held-in-a-module-global-is.md) | bug | Fixed | 4/4 AC(s) verified; critic APPROVE (engineering seat (independent, isolated worktree, closing full-diff review)) |
| [BG0445](../../sdlc-studio/bugs/BG0445-the-test-census-lane-skips-any-path-containing.md) | bug | Fixed | 2/2 AC(s) verified; critic APPROVE (engineering seat (independent, isolated worktree, closing full-diff review)) |
| [US0455](../../sdlc-studio/stories/US0455-one-availability-contract-the-prd-clause-the-tsd.md) | story | Done | 5/5 AC(s) verified; critic APPROVE (product seat (independent, isolated worktree)) |
| [US0557](../../sdlc-studio/stories/US0557-a-batch-invocation-missing-a-required-argument-is.md) | story | Done | 3/3 AC(s) verified; critic APPROVE (engineering seat (independent, isolated worktree)) |
| [US0559](../../sdlc-studio/stories/US0559-the-close-reports-its-own-cost-gate-seconds.md) | story | Done | 4/4 AC(s) verified; critic APPROVE (engineering seat (independent, isolated worktree)) |
| [US0563](../../sdlc-studio/stories/US0563-the-shipped-lifecycle-states-the-batch-boundary-cadence.md) | story | Done | 3/3 AC(s) verified; critic APPROVE (qa seat (independent, isolated worktree)) |
| [BG0454](../../sdlc-studio/bugs/BG0454-the-confinement-write-detector-reads-list-remove-as.md) | bug | Fixed | 3/3 AC(s) verified; critic APPROVE (engineering seat (independent, isolated worktree, closing full-diff review)) |
| [US0453](../../sdlc-studio/stories/US0453-countable-claims-in-the-trd-and-tsd-are.md) | story | Done | 4/4 AC(s) verified; critic APPROVE (qa seat (independent, isolated worktree)) |
| [US0456](../../sdlc-studio/stories/US0456-the-tsd-s-per-script-test-contract-stops.md) | story | Done | 5/5 AC(s) verified; critic APPROVE (product seat (independent, isolated worktree)) |
| [US0460](../../sdlc-studio/stories/US0460-the-porting-doctrine-is-stated-in-one-direction.md) | story | Done | 5/5 AC(s) verified; critic APPROVE (product seat (independent, isolated worktree)) |

## Remaining (0)

_Nothing remains: every unit in the batch reached a terminal status._

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-31 | sdlc-studio | Generated at the run close (`handoff generate`) |
