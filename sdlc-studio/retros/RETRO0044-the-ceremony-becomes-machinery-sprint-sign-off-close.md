# RETRO-0044: The ceremony-becomes-machinery sprint: sign-off, close, re-verdict, the bar and the port made refusing machinery

> **Date:** 2026-07-17
> **Batch:** US0193, US0194, US0195, US0196, US0197, US0198, US0199, US0200 (EP0063-EP0070, from CR0314/0323/0324/0325/0326/0328/0329/0330; RFC0043 all three slices + RFC0044 build)
> **Goal:** done (run RUN-01KXPJG9; Sprint Goal: "Every remaining hand-carried quality ceremony - review sign-off, sprint close, re-verdict, the ready/done bar, forward-port - becomes deterministic, refusing machinery." - judged ACHIEVED via goal-verdict)
> **Delivered:** 8 / 8   **Blocked:** 0
> **Reviewer of record:** Darren Benson (operator) - signed off against the composed decision brief (critic.py signoff-brief via sprint close: the machinery this sprint built, dogfooded at its own close); adversarial passes by the Sam Eriksson QA seat (9 reviews including the closing full-diff pass)

## Delivered

- **US0194 (5pt) - the two-role review gate.** `critic.py evidence` / `signoff` /
  `signoff-brief`; conformance `critiqued` requires evidence plus an independent
  reviewer-of-record sign-off past `review.two_role_after` (adopted here at 192; under
  it, Done means signed off and units hold at Review until the close). Critic REJECT
  round: lint-failing provenance tags, a plan-review-phase delegate hole, a surviving
  evidence-requirement mutant - repaired test-first.
- **US0198 (5pt) - sprint close.** The close ceremony as one deterministic, resumable
  chain ending in the printed decision brief. Critic REJECT round: the real chain
  crashed at step 1 (retro.main takes no argv) behind all-stub tests; a hard-coded
  goal-reached outcome; an unmeasured-cost mutant - repaired, including a no-stub
  real-chain test that guards the break class.
- **US0193 (3pt) - day/sprint-session forecast.** Day buckets default, a
  sprint-session denominator sampled from the velocity history with measured hours,
  ISO week behind a flag. Live read at close: this 8-unit batch forecast "2
  sprint-sessions, ~2.1h" where the week bucket said "next week".
- **US0195 (5pt) - DoR/DoD documents + check-id registry.** Two editable documents,
  tagged criteria resolving through one registry authority, unknown ids loud. CR0332
  filed from the review (near-miss tags silently parse as no tag).
- **US0196 (5pt) - the gates read the documents.** Grooming, transition -> Done,
  conformance review stages, the close and release gates resolve their level's tags;
  absent documents byte-compatible (proven against the shipped templates); every
  downgrade visible. Critic REJECT round: a budget breach and the silent-disarm
  mutant - repaired.
- **US0199 (2pt) - critic brief --rejoinder.** The re-verdict scaffolding made
  deterministic: prior verdict verbatim, the re-execute-your-probes demand, same
  contract. Used live five times inside this very sprint's re-verdict loops.
- **US0197 (3pt) - init DoR/DoD tailoring.** Defaults written at init; a
  stack-derived offer applied only on --accept-tailoring, idempotent on repeat.
  Critic REJECT round: duplicate-on-repeat-accept - repaired RED-first.
- **US0200 (2pt) - forward-port.sh.** The guarded rsync one-liner. Critic REJECT
  round with two PROVEN destructive bypasses (a leaf symlink into the repo; a
  parent-of-repo target) - both refused now; seven-mutant battery, zero survivors.

## Blocked / deferred

- None. 8/8 units delivered; CR0331/CR0332/BG0178 filed as follow-ups, not blockers.

## What went well

- **The machinery reviewed itself.** The rejoinder discipline (US0199) ran five live
  re-verdict loops in the sprint that built it; the sign-off brief (US0194) and the
  close orchestrator (US0198) composed this close's own decision brief.
- **Five of eight units drew an initial REJECT** and every repair went in test-first
  with the reviewer re-executing its own mutants and probes before APPROVE - two
  repairs were proven by live destructive probes (US0200), not by reading.
- **The closing full-diff pass earned its cost** exactly as the doctrine predicts:
  three findings the per-unit reviews were structurally blind to (see Lessons).

## What was hard / what stalled

- **A self-inflicted verifier race:** a TaskStop killed the first mutation run
  mid-mutant, stranding a live mutant in the tree; the second mutation run recorded a
  worthless baseline-red report and the closing critic reviewed the same dirty tree.
  Recovery was clean (checkout, discard, single-writer re-run) but cost a full
  mutation cycle and review round.
- **Cross-unit seams hid in the untested middle:** the two-role x DoD-downgrade
  interaction (both units individually green) silently disarmed the flagship gate for
  a partial tag set.
- **Interactive token spend is still only partially measurable** (CR0278): the
  harness reported per-review subagent totals for initial runs only.

## Lessons

- Never run two tree-mutating verifiers concurrently: a mutation harness owns the
  working tree while it runs, a kill mid-mutant strands a live mutant, and every
  other verifier then measures a lie - single writer, and re-verify the tree after
  any kill. (Validity: 2026-10-17)
- When a gate's requirement has independently-downgradable halves, compose them
  independently and test the partial-tag matrix, not just all-on/all-off - the
  two-role disarm hid in the untested middle row. (Validity: 2026-10-17)
- A composed evidence line must carry its source report's failure state
  (baseline/errors/truncation), not only its successes - otherwise the ceremony
  launders a worthless report into a neutral-looking lane. (Validity: 2026-10-17)

## Estimate vs actual

**Were the estimates any good?** Points delivered 30/30, units 8/8, zero splits or
blocks - the Fibonacci sizing held. The plan forecast 750,000 tokens (30 pts x 25k).
Measured: the harness reported 719,242 subagent tokens across the 9 spawned reviews
(initial runs only - resumed re-verdict turns and the orchestrator session's own spend
are tracked by the harness but not script-readable; CR0278 remains the fix).
Deliberately NOT written into per-unit telemetry: a partial figure in the velocity
ledger would corrupt the tokens-per-point rate (the cross-cohort pooling lesson). The
honest ledger entry is unmeasured-with-a-named-lower-bound.

Mutation evidence (clean re-run at close): baseline pass, 25 applied, 22 killed, 3
survived, 0 errors (survivors: a debug-only stderr guard and two conditional asserts
inside tests - inspected, benign; 4,023 enumerated mutants beyond the ceiling not run).

## Actions raised

To say "nothing worth raising", say so in a row and give the reason. An empty table is
not an answer.

| Finding | Disposition |
| --- | --- |
| Tranche audit blocks extension stories on terminal-epic keywords | CR0331 (filed at plan time) |
| DoR/DoD near-miss check tags silently parse as no tag | CR0332 (filed from the US0195 review) |
| refine's seeded AC headings fail MD026 | BG0178 (filed at plan time) |
| Verifier race: mutation harness vs concurrent reviewers | declined: process not code - ledgered on RUN-01KXPJG9 and recorded as a lesson |
| Interactive sprint token spend only partially measurable | declined: duplicate - CR0278 already tracks the fix |

## Close loop (gated)

`gate --require-retro RETRO0044` (file form) fails until all four are true:

- [x] this retro exists AND passes its content check - required sections, at least one real
      lesson, and every finding dispositioned (`retro.py validate --id RETRO0044`)
- [x] its lessons are in the project store, not just in this file (`retro.py extract --id RETRO0044`)
- [x] open lessons re-validated: each is closed, extended, or within its horizon (`lessons revalidate`)
- [x] `retros/LESSONS-SUMMARY.md` regenerated from the still-valid lessons (`lessons summary`)

The next sprint reads them automatically: `sprint plan` prints the digest in the plan.

## Metrics

- Tokens: 719,242 measured subagent (lower bound; orchestrator share unmeasured, CR0278) · Duration: ~5h elapsed, plan-to-close · Critic rejects: 5 initial + 1 closing (all repaired to APPROVE)

## Handoff

- None owed: the run reached its goal (8/8 terminal at close). Run state closed goal-reached by `sprint close`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | Claude Fable 5 | Written at the RUN-01KXPJG9 close |
