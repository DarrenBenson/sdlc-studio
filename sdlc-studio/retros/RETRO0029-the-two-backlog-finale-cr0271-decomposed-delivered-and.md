# RETRO-0029: The two-backlog finale: CR0271 decomposed, delivered, and closed by its own gate

> **Date:** 2026-07-15
> **Batch:** US0120, US0121, US0122, US0123, US0124, BG0148, BG0149 (EP0033, closing CR0271)
> **Goal:** done
> **Delivered:** 7 / 7   **Blocked:** 0

## Delivered

- **US0120 (5pt) - the request->child link primitive + reconcile verifies both ways (G3).** `sdlc_md`
  now owns `is_request`, `children_of`, `parent_ref`/`child_parent`, `decomposed_ids`; `reconcile`
  reports a one-sided link as `link-asymmetry`. The independent reviewer REJECTED the first cut - a
  real bug (`decomposed_ids` read parenthetical grandchildren as direct children) - which was fixed
  and re-approved. The author != reviewer gate earned its keep on the very first unit.
- **US0121 (2pt) - `sprint plan` refuses an RFC or CR as a sprint unit (G1).** The Delivery backlog is
  stories and bugs. This landed hard: `--crs Proposed` had been the primary planning command for the
  life of the project, so ~26 tests that used CRs as a generic plannable fixture had to migrate to
  delivery units.
- **US0122 (3pt) - a request's successful terminal is DERIVED from its children (G2).** A CR is
  Complete only when its stories/epics are resolved; a childless request cannot be Complete (but may
  still be Rejected). `--force` overrides.
- **US0123 (2pt) - `status backlog` splits the Discovery and Delivery backlogs (G4).** Named
  Discovery/Delivery (dual-track agile / upstream Kanban) by operator decision, over Request/Product -
  "Delivery" does not presume a product.
- **US0124 (2pt) - `reconcile` flags an accepted-but-childless request as `undecomposed` (G5).** Scoped
  to a request PAST intake (an Approved CR / In-Review RFC), so a healthy backlog leaves `reconcile
  detect` clean - the exit-0 contract CI relies on.
- **BG0148 + BG0149 (3pt + 2pt) - artifact.py writes the right sizing field per type.** `--size` for a
  cr/rfc/epic, `--points` for a story/bug, from the same `sdlc_md` writer the filer uses. Closes two
  silent drops (a story's `--points` used to vanish; a CR was written with Points). The wrong flag for
  a type is now warned, never dropped.

## Blocked / deferred

- Nothing blocked. Two DISCOVERY items were RAISED (not delivered - they need decomposition, exactly as
  the gates now enforce): **CR0272** (audit and clean up the command surface; rewrite help around the
  process spine) and **RFC0039** (the discovery track: Issue, refine, triage, dual-track parallel
  roles, Three-Amigos personas, full doc/help/README rewrite).

## What went well

- **CR0271 closed by its own G2 gate.** With all five stories Done and EP0033 Done, `transition CR0271
  -> Complete` passed the derived-status gate CR0271 itself built. The finale closed itself - the
  strongest possible proof the gate works.
- **Independent review caught a real bug the author missed.** US0120's `decomposed_ids` read
  parenthetical annotation ids as direct children; the reviewer refused it, and the same defect had
  earlier been WORKED AROUND (stripping the annotation off CR0271 by hand) rather than fixed. author !=
  reviewer turned a worked-around symptom into a fixed root cause.
- **Decomposition replicated the 1.75x under-sizing finding (LL0038).** CR0271 was single-shot sized at
  8 points; decomposed into stories it summed to 14 - a 1.75x ratio, matching the exact under-sizing
  the RETRO0028 experiment measured. The finale confirmed its own lesson before it was built.
- Every gate was validated against the thing it defends (LL0010): a childless CR was refused
  Complete, a one-sided link was reported, a request batch was refused a plan, an accepted childless CR
  was flagged undecomposed - each proven to FAIL, not just to exist.

## What was hard / what stalled

- **The delivery was interactive, so per-unit token actuals were NOT captured.** This sprint was driven
  by hand rather than through the autosprint runner that measures tokens per unit, so the estimate vs
  actual table below is UNMEASURED. The velocity evidence this sprint carries is the DECOMPOSITION (14
  points from a single-shot 8), not a measured tokens-per-point rate. Do not read a rate from this
  sprint; the next runner-driven, decomposition-sized sprint is the real out-of-sample test.
- **G1 rippled widely.** Because CR-planning was the suite's primary test vehicle, ~26 tests across
  test_sprint / test_retro / test_points_model, then test_artifact / test_create_validate_roundtrip /
  test_invariants / test_points, had to migrate from CRs to delivery units. Each was the old workflow
  the gate abolishes; none was a CR-specific planning test.
- The size model's creation path change (a CR carries Size, not Points) refused a CR created the old
  way - correct, but it surfaced everywhere the tests minted a CR with points.

## Lessons

- A worked-around symptom is a bug you have not found yet. US0120's parenthetical defect was first met
  by hand-editing the artefact that triggered it (stripping the annotation off CR0271); an independent
  reviewer, not the author, is what turned that workaround into a root-cause fix. Verify by an
  independent actor attacking the claim, not the author re-reading it.
- A gate that changes the canonical creation path ripples into every test that used the old path as a
  generic fixture. Budget the migration as part of the gate, not as a surprise: the ripple is the
  measure of how load-bearing the old behaviour was.
- Decomposition makes the estimate accurate (LL0038 again): a single-shot CR sized 8 decomposed to 14,
  the same 1.75x the prior experiment found. The way to a good forecast is smaller, decomposed units -
  not a cleverer single-shot guess.

## Estimate vs actual

**Were the estimates any good?** UNMEASURED this sprint. The batch was delivered interactively, not
through the token-measuring runner, so no per-unit actuals were recorded. The plan forecast 475,000
tokens (19 points x the 25,000 seed); there is no measured actual to compare it against, and none is
invented here. An unmeasured unit is never counted as accurate.

<!-- accuracy:begin (generated by retro.py accuracy --write) -->
<!-- accuracy:end -->

The one number this sprint does carry is the decomposition ratio: CR0271 single-shot 8 -> decomposed
14 = 1.75x, replicating RETRO0028's under-sizing finding on a fresh unit. That is evidence about
SIZING, not about the rate. The rate's out-of-sample test is the next runner-driven sprint whose units
were sized by decomposition.

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the issues found?**

| Finding | Disposition |
| --- | --- |
| artifact.py: a cr given an OFF-scale wrong `--points` (e.g. `--points 7 --size M`) is hard-refused with a Points-scale error rather than the intended "wrong flag - pass --size" warning; no bad artefact is written either way | declined: a confusing message on invalid input, not a correctness defect (the reviewer confirmed no artefact is mis-written). Low priority; fold into CR0272's artifact.py pass rather than a standalone ticket. |
| The command surface has accreted superseded routes; help does not foreground the process spine | CR0272 (raised) |
| The discovery track is incomplete: no Issue type, no first-class refine/triage, personas not fully baked into refine/triage/review, docs not updated | RFC0039 (raised) |
| Per-unit token actuals are not captured on an interactively-driven sprint | declined: not a defect - the runner captures them; this sprint was hand-driven by choice. Noted in the retro so the rate is not misread. |

## Close loop (gated)

- [x] this retro exists AND passes its content check
- [x] its lessons are in the project store
- [x] open lessons re-validated
- [x] `retros/LESSONS-SUMMARY.md` regenerated

## Metrics

- Tokens: UNMEASURED (interactive session, no per-unit telemetry) - Duration: one session - Critic rejects: 1 (US0120, fixed and re-approved)
