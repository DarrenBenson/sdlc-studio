# HO-0070: every Medium open at this run's base ref is disposed of - terminal with its own verifiers passing, or ruled open with a date and a reason - and so is any this run itself files

> **Date:** 2026-09-10
> **Created-by:** sdlc-studio new
> **Run:** RUN-01M20RWX (started 2026-09-08T14:58:10Z)
> **Outcome:** goal-reached
> **Goal:** done
> **Batch source:** argument

## Where to pick up

Every unit in the batch is terminal. There is no tail: close the run and plan the next batch normally.

## Appetite

- **Declared:** wall-clock 5760 min, units 64 unit(s)
- **Spent:** 3291.4 min, 22 unit(s) terminal
- **Delivered:** 22 unit(s)
- **Token forecast:** ~4,299,335 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (22)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0490](../../sdlc-studio/bugs/BG0490-four-bug-repairs-are-fixed-with-half-their.md) | bug | Fixed | 5/5 AC(s) verified; critic REJECT (product seat) |
| [BG0493](../../sdlc-studio/bugs/BG0493-four-more-verifiers-pass-on-a-delivery-that.md) | bug | Fixed | 5/5 AC(s) verified; critic REJECT (qa seat) |
| [BG0567](../../sdlc-studio/bugs/BG0567-the-upgrading-project-baseline-compares-against-this-tree.md) | bug | Fixed | 5/5 AC(s) verified; critic APPROVE (qa seat (fresh-context subagent, delivery round 1)) |
| [BG0578](../../sdlc-studio/bugs/BG0578-test-file-attribution-is-decided-by-name-frequency.md) | bug | Fixed | 6/6 AC(s) verified; critic REJECT (qa seat) |
| [BG0591](../../sdlc-studio/bugs/BG0591-status-and-close-owed-give-opposite-answers-about.md) | bug | Fixed | 5/5 AC(s) verified; critic REJECT (qa seat) |
| [BG0601](../../sdlc-studio/bugs/BG0601-the-dry-run-class-sweep-compares-only-the.md) | bug | Fixed | 3/3 AC(s) verified; critic REJECT (qa seat) |
| [BG0608](../../sdlc-studio/bugs/BG0608-the-budget-line-still-leads-with-the-seconds.md) | bug | Fixed | 4/4 AC(s) verified; critic REJECT (product seat) |
| [BG0612](../../sdlc-studio/bugs/BG0612-three-limbs-that-survived-the-closure-of-bg0599.md) | bug | Fixed | 4/4 AC(s) verified; critic REJECT (qa seat (fresh-context subagent, delivery round 1)) |
| [BG0627](../../sdlc-studio/bugs/BG0627-eleven-other-fields-file-consumers-carry-the-same.md) | bug | Fixed | 5/5 AC(s) verified; critic APPROVE (product seat (fresh-context subagent, delivery round 1)) |
| [BG0630](../../sdlc-studio/bugs/BG0630-the-test-plan-gate-is-skipped-on-in.md) | bug | Fixed | 6/6 AC(s) verified; critic REJECT (product seat (fresh-context subagent, delivery round 1)) |
| [BG0633](../../sdlc-studio/bugs/BG0633-transition-py-annotate-is-a-third-writer-of.md) | bug | Fixed | 4/4 AC(s) verified; critic REJECT (qa seat (fresh-context subagent, delivery round 1)) |
| [BG0637](../../sdlc-studio/bugs/BG0637-critic-clean-escapes-underscores-inside-code-spans-corrupting.md) | bug | Fixed | 6/6 AC(s) verified; critic REJECT (qa seat) |
| [BG0654](../../sdlc-studio/bugs/BG0654-a-push-whose-pre-push-gate-outlives-the.md) | bug | Fixed | 3/3 AC(s) verified; critic REJECT (product seat) |
| [BG0655](../../sdlc-studio/bugs/BG0655-a-mutant-survives-at-claude-skills-sdlc-studio.md) | bug | Fixed | 3/3 AC(s) verified; critic APPROVE (qa seat (fresh-context subagent, delivery round 1)) |
| [BG0656](../../sdlc-studio/bugs/BG0656-the-disclosure-page-s-prose-and-its-guard.md) | bug | Fixed | 3/3 AC(s) verified; critic REJECT (product seat (fresh-context subagent, delivery round 1)) |
| [BG0657](../../sdlc-studio/bugs/BG0657-the-scheduled-corpus-lane-is-red-at-23.md) | bug | Fixed | 6/6 AC(s) verified; critic REJECT (engineering seat (fresh-context subagent, delivery round 1)) |
| [US0819](../../sdlc-studio/stories/US0819-the-plan-probe-runs-each-criterion-against-the.md) | story | Done | 9/9 AC(s) verified; critic REJECT (qa seat (fresh-context subagent, delivery round 1)) |
| [US0820](../../sdlc-studio/stories/US0820-sprint-plan-refuses-a-batch-carrying-an-unruled.md) | story | Done | 6/6 AC(s) verified; critic REJECT (product seat (fresh-context subagent, delivery round 1)) |
| [US0821](../../sdlc-studio/stories/US0821-the-plan-ruling-is-recorded-hashed-against-what.md) | story | Done | 8/8 AC(s) verified; critic REJECT (qa seat (fresh-context subagent, delivery round 1)) |
| [BG0658](../../sdlc-studio/bugs/BG0658-testplan-derive-writes-its-rows-unescaped-and-reads.md) | bug | Fixed | 5/5 AC(s) verified; critic REJECT (qa seat) |
| [US0822](../../sdlc-studio/stories/US0822-a-ledger-row-records-the-anchor-it-was.md) | story | Done | 9/9 AC(s) verified; critic REJECT (qa seat (fresh-context subagent, delivery round 1)) |
| [BG0660](../../sdlc-studio/bugs/BG0660-the-rehearsal-lane-test-drives-the-whole-boundary.md) | bug | Fixed | 4/4 AC(s) verified; critic REJECT (qa seat (fresh-context subagent, delivery round 1)) |

## Remaining (0)

_Nothing remains: every unit in the batch reached a terminal status._

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-10 | sdlc-studio | Generated at the run close (`handoff generate`) |
