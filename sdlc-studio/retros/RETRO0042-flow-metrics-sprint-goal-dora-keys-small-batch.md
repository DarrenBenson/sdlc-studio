# RETRO-0042: Flow metrics, Sprint Goal, DORA keys, small-batch guard - the agile-gap tranche

> **Date:** 2026-07-16
> **Batch:** US0180, US0181, US0182, US0183, US0184, US0185 (EP0052-EP0055, from CR0310-CR0313)
> **Goal:** done (run RUN-01KXGPBN, planned at --goal plan, driven to done on operator go)
> **Delivered:** 6 / 6   **Blocked:** 0
> **Reviewer of record:** Darren Benson (operator) - signed off 2026-07-16; adversarial passes by the Dani Okafor and Sam Eriksson seats (subagents, RFC0044)

## Delivered

- **US0180 (5pt) - flow compute.** Per-unit cycle time (Created -> delivered from git, anchored
  -G header regex after the critic's pickaxe-poison catch), weekly throughput (delivered statuses
  only), work-item age; unresolvables NAMED. The zero-token schedule instrument.
- **US0181 (2pt) - blocked-age + ageing flags.** Blocked-age distinct from total age (revision
  fallback REFUSED for transient statuses); status ageing advisory behind `flow.ageing_days`,
  off by default.
- **US0182 (3pt) - Monte Carlo forecast.** Seeded 50/85/95% completion dates from measured weekly
  throughput, zero weeks included; refuses on thin/all-zero history, non-positive batches, and
  horizon-capped ranks. Sprint report shows the flow axis; schedule-vs-cost vocabulary fixed.
- **US0183 (3pt) - Sprint Goal.** One product-outcome sentence recorded at plan (never invented,
  never erased by a re-plan), judged at close via `goal-verdict`, displayed on the report.
- **US0184 (3pt) - DORA four keys.** `deploy metrics` from the ledger + git + bug dates; absent
  sources UNMEASURABLE by name; not-applicable without a ledger; deploy keeps never-shells-out.
- **US0185 (3pt) - small-batch guard.** Advisory `batch-size` gate lane (diff lines/files vs
  configured thresholds, end-anchored commit attribution), warn-only in every path, off by default.

## Blocked / deferred

- Nothing blocked. CR0310-CR0313 Complete; EP0052-EP0055 Done.

## What went well

- **The independence gate earned its cost five times in one sprint.** 5 of 6 units drew an
  initial REJECT or blocking-grade findings from the seat critics, every one a real defect the
  author could not see: the git pickaxe poison (live on 3 workspace files), a mid-run re-plan
  erasing the Sprint Goal, a tty prompt that would hang the pre-commit hook, a symmetric fixture
  that let a CFR classifier mutant pass green, and a horizon-capped forecast presented as real
  dates. All repaired with mutation-verified regression tests before Done.
- **The grooming and commit gates fired correctly on the plan's own artefacts** (Affects naming
  only not-yet-existing files; placeholder-scaffold stories refused at commit) - CR0309's case
  made concrete twice.
- **Deterministic instruments dogfooded immediately:** the forecast priced this very sprint
  (19pts, 50% by 2026-07-23 at week granularity) and exposed its own granularity flaw within
  the hour (see Lessons -> CR0314).

## What was hard / what stalled

- **Critic availability:** one seat review died on a 529 server overload and needed a resend;
  another lost its first run to the session limit earlier in the day. Resume-by-message worked
  both times.
- **The changed-surface mutation sampler mis-scopes easily:** run with a flow-only suite over
  the whole diff it reported 19 phantom survivors; scoped to flow.py it reported honestly
  (20/25 killed, 3 boundary-trim survivors in the revision-fallback section parser).

## Lessons

- Calibrate an instrument's units to the measured process, not the literature's default: the MC
  forecast shipped with ISO-week buckets from human-team Kanban canon while this repo's own
  measured cycle time is 0 days and sprints are hour-scale sessions - the operator caught it at
  the close (CR0314: sprint-session and day buckets).
- A reporting cap is a refusal in disguise: any bounded simulation/measurement that can hit its
  bound must refuse or flag at the bound, never present the capped value as measured (the
  MC_WEEK_CAP catch - same class as the RFC0041 reporting-honesty MAJORs).
- A shared measurement helper (`flow.terminal_date`) grown for one status class (terminal) needs
  its assumptions re-checked per caller: the revision-row fallback that is sound for Done is a
  guess for Blocked - the fallback became opt-out per call site.

## Estimate vs actual

**Were the estimates any good?** The plan forecast 475,000 tokens (19pts x 25k seed rate,
plausible 237k-1,078k). Per-unit telemetry is not recorded for an interactive sprint; the
harness-tracked sprint total is awaited from the operator (`retro.py accuracy --id RETRO0042
--tokens N --write`) - reported as **not-yet-captured**, never unknowable. Subagent spend alone
(5 seat critics + re-verdicts) measured ~495k tokens, already at the point-forecast, so the
full actual will land above it - consistent with the review-heavy shape of this batch (5
REJECT-repair cycles).

## Actions raised

| Finding | Disposition |
| --- | --- |
| Weekly buckets wrong for agent-speed delivery (operator direction) | CR0314 |
| Mutation sampler mis-scope (whole-diff targets vs narrow suite) reads as phantom survivors | declined: operator error documented here; revisit only if it recurs |

## Close loop (gated)

`gate --require-retro RETRO0042` (this retro's id, file form) fails until all four are true:

- [x] this retro exists AND passes its content check - required sections, at least one real
      lesson, and every finding dispositioned (`retro.py validate --id RETRO0042`)
- [x] its lessons are in the project store, not just in this file (`retro.py extract --id RETRO0042`)
- [x] open lessons re-validated: each is closed, extended, or within its horizon (`lessons revalidate`)
- [x] `retros/LESSONS-SUMMARY.md` regenerated from the still-valid lessons (`lessons summary`)

The next sprint reads them automatically: `sprint plan` prints the digest in the plan.

## Metrics

- Tokens: not-yet-captured (subagent share ~495k measured; operator to supply the harness total) · Duration: single interactive session 2026-07-16 evening · Critic rejects: 3 REJECT->APPROVE cycles + 2 APPROVE-with-blocking-grade-findings-fixed (5 of 6 units repaired under review)

## Handoff

- [HO-0001](../handoffs/HO0001-agile-gap-tranche-delivered-cr0314-sprint-hour-forecast.md) - 0 remaining item(s): 0 copilot-tail, 0 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-16 | Claude Fable 5 | Sprint close: 6/6 delivered, lessons + dispositions recorded |
| 2026-07-16 | Darren Benson (operator) | Reviewer-of-record sign-off (AskUserQuestion); token actual left not-yet-captured |
