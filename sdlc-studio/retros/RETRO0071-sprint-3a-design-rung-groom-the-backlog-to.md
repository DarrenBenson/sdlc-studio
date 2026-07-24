# RETRO-0071: Sprint 3a design rung - groom the backlog to a provable red-now bar

> **Date:** 2026-07-24
> **Batch:** US0345, US0346, US0347, US0348, US0349, US0350, US0351, US0352, US0355, US0356, US0359, US0360, US0367, US0368, US0369, US0370, US0413, US0414
> **Goal:** Every remaining backlog story carries authored acceptance criteria and an executable Verify line, so the delivery sprint that empties the backlog can be planned against a groomed backlog rather than a guess.
> **Delivered:** 18 / 18   **Blocked:** 0

## Delivered

- **All 18 skeleton stories groomed** - 41 acceptance criteria authored with Given/When/Then and a node-addressed Verify line, and all 18 transitioned Draft to Ready.
- **A red-now ledger with pass=0, fail=41, manual=0.** This is the whole point of a design rung: the behaviour is absent, so running every verifier costs nothing and the counterfactual bar is PROVED rather than asserted. A criterion that passes before its code exists is worthless, and there is no other moment when that is cheap to check.
- **Four operator decisions recorded and decomposed** - D0059-D0062, 13 stories and 4 epics across EP0157-EP0160. The discovery backlog now holds nothing undecided except CR0355, which is deliberately held until the v5 launch.
- **The grooming pre-work the planner demanded** - BG0282 split from 13 points into three units, and `Affects` derived for 27 stories.

## Blocked / deferred

- **Nothing blocked.** The 13 stories the decisions created (US0419-US0431) are ungroomed and are the immediate follow-on - see the goal verdict below.

## What went well

- **The red-now ledger earned the rung on its first run.** Three of 41 verifiers PASSED against unbuilt behaviour. All three were the same defect - a check matching text already in the tree - and none would have been caught by reading them. `check_versions --strict` asserted CONSISTENCY, green at 4.1.0 and green at any consistent version; `grep xrepo` matched a word BG0162 had already written; `grep Primary` matched the one-Primary-per-interface constraint while the story exists precisely because no selection METHOD does.
- **Every refusal the tooling produced was correct**, and each cost less than the mistake it prevented: the 13-point split, the ungroomed-batch gate, the discovery-items-are-not-work gate, `--fresh` with `--from-run` (US0395's own fix, firing on its author), and the requirement that a Sprint Goal be seat-reviewed before it can be planned.
- **BG0270's fix confirmed in the wild.** All three seats classed the batch as themed rather than one increment, and the planner carried that as advice instead of refusing the plan - which is exactly the behaviour that bug bought.

## What was hard / what stalled

- **I diagnosed BG0290 wrongly and built a workaround on the wrong diagnosis.** The first read blamed `--epic-title` versus `--into`, because four stories refined in the same minute passed and two failed. The workaround - mint the epic first, then refine into it - was applied to three RFCs and all 13 resulting stories failed identically. The real trigger is whether the REQUEST carries ACs to seed from: a CR does, an RFC has Design Options and does not. Refining any accepted RFC is blocked.
- **My first repair of a vacuous verifier was itself vacuous.** US0352's replacement used a `[^.]*` regex against a sentence that contains a line break, so it matched nothing and passed. Caught by re-running the ledger, not by re-reading the pattern - the same way the original was caught.
- **Grooming had to be done outside any unit.** 27 hand-edited artefacts and a 13-point split, with no story behind them, no estimate and no review. Filed as CR0418 and ruled on the same day.
- **Deciding requests grew the backlog before it could shrink.** 104 to 120 non-terminal. Correct behaviour - four decisions became real work - but it means the run's own goal was falsified by the run's own progress.

## Lessons

- **A verifier that matches text already in the tree proves nothing, and reading it will not tell you.** Three of 41 passed here and a fourth passed after being repaired. The only reliable detector is running every verifier at the moment the behaviour is absent and requiring pass=0 - which is free exactly once, at a design rung, and impossible afterwards.
- **A wrong diagnosis does not fail loudly - it produces a workaround that fails silently.** BG0290's first diagnosis was plausible, fitted the evidence available, and sent 13 stories through a fix that could not work. Before building on a diagnosis, find the case it predicts will behave differently and check that it does.
- **Deciding a request is not the same as reducing the backlog.** Four rulings converted 9 discovery items into 17 delivery units. A backlog count is not a progress measure while any decisions are outstanding.

## Estimate vs actual

**Were the estimates any good?** The plan forecast a token cost per unit; telemetry recorded
what each one actually cost. This section holds the comparison, so the question is asked every
sprint instead of only when someone remembers to ask it.

Generate it: `scripts/retro.py accuracy --id RETROxxxx --write` - it fills the block below from
the batch's telemetry and appends this sprint's row to `retros/VELOCITY.md`.

A unit with no per-unit telemetry record has its PER-UNIT ratio reported as **UNMEASURED** and
excluded from that ratio - it is never counted as accurate. But the token count itself is NOT
unmeasurable: the harness tracks it deterministically. An INTERACTIVE sprint (no runner) records no
per-unit actual, so the close captures this RUN's share of the harness-tracked total itself
(`accuracy --tokens-from-harness`, run by `sprint close --apply-signoff`) and the velocity row
records it. The meter is per-SESSION and cumulative, so what is captured is the delta from the
baseline stamped when the run opened - not the session total, which in a session holding more than
one sprint counts the earlier ones again. A run with no baseline (opened before the baseline
existed, or closed from a different session) reports **not-attributable** rather than a number:
there is no fallback to the raw total, because a plausible-looking figure that is not this sprint's
cost is worse than an absent one. When the capture cannot attribute, the close states why and
`accuracy --tokens N` remains the manual override.
Report it as **not-yet-captured** only while neither has happened, never as if the number were
unknowable. That figure is DESCRIPTIVE, never a target (see CR0273).

The forecast is a hypothesis, not a settled calibration. Read the ratio, write down what it
implies, and change the constants only on evidence a human has looked at - a fit to a couple of
sprints fits noise.

<!-- accuracy:begin (generated by retro.py accuracy --write) -->
<!-- accuracy:end -->

- {{what the ratio implies - which units the estimate missed, and why}}

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the
issues found?**

This is the question that turns a retro into work. Every finding gets a disposition:
**file it**, or **decline it with a reason**. Both are green. What does not pass is
silence - a finding written down and left to rot.

To say "nothing worth raising", say so in a row and give the reason. An empty table is
not an answer.

| Finding | Disposition |
| --- | --- |
| Three of 41 verifiers passed against unbuilt behaviour (`check_versions --strict` asserting consistency not value; `grep xrepo`; `grep Primary`) | declined: fixed in-sprint under RUN-01KYA8CF - each criterion repaired and the reason recorded in the criterion itself |
| A repaired verifier was itself vacuous: US0352's `[^.]*` regex cannot cross the line break the target sentence contains | declined: fixed in-sprint under RUN-01KYA8CF - re-anchored on the exact phrase and re-run to confirm it fails today |
| Refining any accepted RFC produces stories that cannot be committed - the request has no ACs to seed from, so validate's no-ac error fires on refine's own output | BG0290 |
| refine's seeded ACs duplicate their label and restate the story title as the Then clause | BG0291 |
| Grooming debt is clearable only by unbatched hand-work: the breakdown gate refuses every plan including the design rung meant to produce the grooming | CR0418 |
| BG0290's first diagnosis was wrong (--epic-title vs --into) and the workaround built on it silently failed for 13 stories | declined: the bug's diagnosis was corrected in place rather than a second bug filed - a wrong diagnosis on an open bug is an edit, not a new defect |
| The capacity ceiling (1M tokens / 8 units / 240 min) is stale against the last four sprints, so every plan reports OVER BUDGET and the warning stops being read | CR0419 |
| The sprint goal was falsified by the run's own progress - 13 stories created mid-run by the operator's decisions are ungroomed | declined: recorded as the goal verdict (partial) with the count, not as a defect - the run has no amendment path and adding to a fixed batch would be the wrong fix |
| A design rung's forecast reports the fixed term only, so it reads identically for 18 units and for 43 and cannot size the rung | declined: correct behaviour under the rung-awareness fix - the marginal rate for a design rung is genuinely unmeasured, and a second data point exists only after this retro |

<!-- file one with: scripts/file_finding.py · check with: scripts/retro.py dispose --id RETROxxxx -->

## Close loop (gated)

`gate --require-retro RETROxxxx` (this retro's id, file form) fails until all four are true:

- [ ] this retro exists AND passes its content check - required sections, at least one real
      lesson, and every finding dispositioned (`retro.py validate --id RETROxxxx`)
- [ ] its lessons are in the project store, not just in this file (`retro.py extract --id RETROxxxx`)
- [ ] open lessons re-validated: each is closed, extended, or within its horizon (`lessons revalidate`)
- [ ] `retros/LESSONS-SUMMARY.md` regenerated from the still-valid lessons (`lessons summary`)

The next sprint reads them automatically: `sprint plan` prints the digest in the plan.

## Metrics

- Tokens: {{tokens}} · Duration: {{duration}} · Critic rejects: {{rejects}}
