# RFC-0050: An adversarial pass over the sprint plan and test plan before the build starts

> **Status:** Accepted
> **Decomposed-into:** EP0158
> **Size:** L
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/critic.py,.claude/skills/sdlc-studio/reference-sprint.md
> **Date:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Every adversarial surface this project has runs AFTER code exists: the per-unit critic judges a diff, the close runs a full-diff refutation pass, and critic.py's seven subcommands are all post-build. The planner's own checks are mechanical only - shared-file clusters, WSJF ordering, capacity, origin drift - and none of them asks whether the batch is the RIGHT batch. The consequence is that the cheapest possible finding, 'this unit does not need to be built', can only be discovered by building it. This RFC proposes a bounded adversarial pass over the plan itself, before --write, across three lenses. SCOPE: does each unit need to exist, and is it already served by something in the codebase, the stdlib, or an installed dependency - the scope lens deliberately borrows the decision ladder from Ponytail (github.com/DietrichGebert/ponytail, MIT, (c) 2026 DietrichGebert), whose seven rungs are a ready-made refutation script for a work item. RISK: does the batch's declared proof strategy match what the units actually touch, which is the plan-time half of RFC0049. EFFICIENCY: would refactoring the code or the tests this batch touches pay for itself WITHIN the sprint, so an accepted cost is chosen rather than absorbed. Output is a findings list under the same disposition discipline the retro already enforces - every finding is filed or declined with a reason, and silence is not an answer - so the pass informs the plan without blocking it. The pass is intensity-scaled to batch size (Ponytail's lite/full/ultra idea) because it spends tokens before any value is delivered, on a sprint whose length is already the standing complaint. Two honest costs: a plan critic has strictly LESS information than the builder will have, so its findings are cheaper to act on but more speculative; and Ponytail's published gains are self-reported over 12 tasks on a single repository with no control methodology stated, so the technique should be adopted on its reasoning and re-measured here, never cited as an established rate.

## Design Options

- **A: no change - the plan stays mechanically checked, and scope, proof and efficiency findings continue to surface during the build or at the close. Costs nothing at plan time. Keeps paying the full build cost for work that a five-minute read would have cut, which is the most expensive place to learn it.**
- **B: one bounded plan-critic pass, three fixed lenses (scope / risk / efficiency), intensity-scaled to batch size, emitting findings the planner must dispose of before --write. Single stage, single artefact, reuses the retro's existing file-or-decline discipline. The three lenses stay coupled, so a batch needing only a scope check still pays for all three unless intensity handles it.**
- **C: three separate seat-owned passes - Product Owner refutes scope, QA refutes the proof strategy, Engineering assesses refactoring - each recorded under its seat like the close-time critic. Richest signal and the cleanest audit trail. Three stages before any code is written, on the sprint length already under complaint.**

## Recommendation

B, gated behind RFC0048 option B landing first. The scope lens alone is the cheapest speed lever available: unbuilt work costs nothing, and every other lever in flight only makes work go faster. Adopt Ponytail's ladder as the scope lens's refutation script with its MIT notice carried, adopt its intensity control as the cost governor, and adopt its deferred-shortcut ledger as the place efficiency findings go when declined - but re-measure any gain against this repo's own velocity series rather than importing its numbers. Escalate to C only if B's findings show one lens consistently starved by the other two.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Choose between: A: no change - the plan stays mechanically checked, and scope, proof and efficiency findings continue to surface during the build or at the close. Costs nothing at plan time. Keeps paying the full build cost for work that a five-minute read would have cut, which is the most expensive place to learn it., B: one bounded plan-critic pass, three fixed lenses (scope / risk / efficiency), intensity-scaled to batch size, emitting findings the planner must dispose of before --write. Single stage, single artefact, reuses the retro's existing file-or-decline discipline. The three lenses stay coupled, so a batch needing only a scope check still pays for all three unless intensity handles it. or C: three separate seat-owned passes - Product Owner refutes scope, QA refutes the proof strategy, Engineering assesses refactoring - each recorded under its seat like the close-time critic. Richest signal and the cleanest audit trail. Three stages before any code is written, on the sprint length already under complaint. | CLOSED: **B** - one bounded plan-critic pass before `--write`, three fixed lenses, intensity-scaled, findings filed or declined. Ruled by the operator 2026-07-24, recorded as D0061, decomposed into EP0158. |

## Decision

**B** - recorded as [D0061](../decisions.md) on 2026-07-24 by Darren Benson (operator).

One bounded plan-critic pass before `--write`: three fixed lenses, intensity-scaled, findings disposed of under the retro's file-or-decline discipline.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
