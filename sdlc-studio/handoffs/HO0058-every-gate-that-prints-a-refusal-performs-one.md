# HO-0058: Every gate that prints a refusal performs one, and the acceptance criteria the README says are executable and get run do run

> **Date:** 2026-08-15
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KZQ03V (started 2026-08-10T23:37:24Z)
> **Outcome:** goal-reached
> **Batch source:** run-state.json

## Where to pick up

Every unit in the batch is terminal. There is no tail: close the run and plan the next batch normally.

## Appetite

- **Declared:** wall-clock 7200 min, units 27 unit(s)
- **Spent:** 6225.4 min, 19 unit(s) terminal
- **Delivered:** 19 unit(s)
- **Token forecast:** ~2,642,963 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (19)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0535](../../sdlc-studio/bugs/BG0535-106-of-1824-executable-acceptance-criteria-are-red.md) | bug | Fixed | 3/3 AC(s) verified; critic APPROVE (engineering; independent adversarial pass; fresh context) |
| [BG0536](../../sdlc-studio/bugs/BG0536-a-test-fixture-that-accepts-a-caller-supplied.md) | bug | Fixed | 2/2 AC(s) verified; critic REJECT (engineering; independent adversarial pass; fresh context) |
| [BG0542](../../sdlc-studio/bugs/BG0542-sprint-plan-under-affects-check-block-prints-refused.md) | bug | Fixed | 2/2 AC(s) verified; critic APPROVE (engineering; independent adversarial pass; fresh context) |
| [BG0543](../../sdlc-studio/bugs/BG0543-the-warning-ratchet-still-exits-0-on-a.md) | bug | Fixed | 3/3 AC(s) verified; critic REJECT (engineering; independent adversarial pass; fresh context) |
| [BG0557](../../sdlc-studio/bugs/BG0557-sprint-close-dry-run-reports-a-checklist-stop.md) | bug | Fixed | 2/2 AC(s) verified; critic APPROVE (engineering; independent adversarial pass; fresh context) |
| [US0667](../../sdlc-studio/stories/US0667-every-writer-refuses-a-verify-selector-that-resolves.md) | story | Done | 3/3 AC(s) verified; critic APPROVE (engineering; independent adversarial pass; fresh context) |
| [US0668](../../sdlc-studio/stories/US0668-a-selector-that-cannot-be-judged-is-accepted.md) | story | Done | 2/2 AC(s) verified; critic APPROVE (engineering; independent adversarial pass; fresh context) |
| [US0669](../../sdlc-studio/stories/US0669-validate-sweeps-the-existing-corpus-for-unresolvable-selectors.md) | story | Done | 2/2 AC(s) verified; critic APPROVE (engineering; independent adversarial pass; fresh context) |
| [BG0406](../../sdlc-studio/bugs/BG0406-three-units-delivered-nothing-bg0372-writes-no-velocity.md) | bug | Fixed | 8/8 AC(s) verified; critic REJECT (engineering; independent adversarial pass; fresh context) |
| [BG0457](../../sdlc-studio/bugs/BG0457-four-spec-agreement-guards-pin-prose-to-prose.md) | bug | Fixed | critic APPROVE (engineering; independent adversarial pass; fresh context) |
| [BG0469](../../sdlc-studio/bugs/BG0469-close-owed-reports-a-close-that-already-happened.md) | bug | Fixed | critic APPROVE (engineering; independent adversarial pass; fresh context; round 2) |
| [BG0488](../../sdlc-studio/bugs/BG0488-us0608-and-us0609-ship-a-feature-no-cli.md) | bug | Fixed | critic APPROVE (engineering; independent adversarial pass; fresh context; round 2) |
| [BG0497](../../sdlc-studio/bugs/BG0497-three-units-ship-a-check-whose-own-criterion.md) | bug | Fixed | critic REJECT (engineering; independent adversarial pass; fresh context) |
| [BG0522](../../sdlc-studio/bugs/BG0522-bg0515-s-fix-reproduces-bg0515-a-charter-with.md) | bug | Fixed | critic APPROVE (engineering; independent adversarial pass; fresh context) |
| [BG0523](../../sdlc-studio/bugs/BG0523-five-acceptance-criteria-are-pinned-by-verifiers-that.md) | bug | Fixed | critic APPROVE (engineering; independent adversarial pass; fresh context) |
| [BG0528](../../sdlc-studio/bugs/BG0528-a-delivered-unit-left-at-ready-is-invisible.md) | bug | Fixed | critic APPROVE (engineering; independent adversarial pass; fresh context) |
| [BG0566](../../sdlc-studio/bugs/BG0566-npm-run-lint-fix-destroys-an-artefact-whose.md) | bug | Fixed | critic APPROVE (engineering; independent adversarial pass; fresh context) |
| [BG0569](../../sdlc-studio/bugs/BG0569-nothing-stops-a-tool-or-fixture-writing-into.md) | bug | Fixed | critic APPROVE (engineering; independent adversarial pass; fresh context) |
| [US0670](../../sdlc-studio/stories/US0670-the-release-discloses-every-open-medium-and-low.md) | story | Done | 7/7 AC(s) verified; critic APPROVE (engineering; independent adversarial pass; fresh context) |

## Remaining (0)

_Nothing remains: every unit in the batch reached a terminal status._

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-15 | sdlc-studio | Generated at the run close (`handoff generate`) |
