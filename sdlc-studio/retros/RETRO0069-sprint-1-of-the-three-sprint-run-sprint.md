# RETRO-0069: Sprint 1 of the three-sprint run - sprint-engine upgrade (8 epics, 19 stories)

> **Date:** 2026-07-23
> **Batch:** US0371, US0391, US0392, US0393, US0398, US0399, US0400, US0401, US0402, US0403, US0404, US0405, US0406, US0407, US0408, US0409, US0410, US0411, US0412
> **Goal:** A themed batch that stops eight sprint-engine tools being hand-driven, each independently verified, so sprints 2 and 3 run on instruments they can trust.
> **Delivered:** 19 / 19   **Blocked:** 0

## Delivered

- EP0130 (US0371) - `sprint plan` flags a green Draft story built-not-closed and excludes it from the build forecast; an all-built batch points at the close path.
- EP0151 (US0400-0401) - the token forecast prices the rung: a `--goal design` run reads UNMEASURED for the marginal term instead of borrowing the build rate; a non-done close records tokens with the rate left blank.
- EP0150 (US0398-0399) - atomic three-surface artefact retitle (H1, filename, index row) with inbound-reference rewrite and a recorded old title.
- EP0155 (US0410-0412) - refine mints a plannable unit: an Affects is required or inherited per story, and an ungroomed story carries an explicit machine-visible marker.
- EP0154 (US0407-0409) - `sprint plan` offers sequential or parallel delivery only when the batch decomposes into file-disjoint groups; test files count as coupling; the choice is deterministic and recorded.
- EP0146 (US0391-0393) - critic, close_owed and sprint prose reach their creation scripts via a shared `--fields-file` loader without crossing a shell; the flag path reports a detected shell hazard; telemetry confirmed safe-by-nature.
- EP0152 (US0402-0403) - goal review distinguishes an amendment (carries the requesting seat's verdict forward, records the trail) from a material change (nothing carries), the operator's declaration recorded.
- EP0153 (US0404-0406) - a deterministic seat brief composed from the plan and lessons registry, recorded with the verdicts; goal-review reads seats and notes from a fields-file.

## Blocked / deferred

- None. All 19 units reached Review; Done is owed to the operator sign-off (two-role gate, `review.two_role_after: 192`).

## What went well

- The independent 3-reviewer adversarial panel (fresh contexts over disjoint slices of the ~2137-line diff) earned its keep: it found 7 real defects, 1 MAJOR, that every per-story test had passed over. Adversarial review before sign-off is where the truth surfaces.
- The engine dogfooded itself throughout: the mint-time Affects gate refused a bad bug filing; the engagement-floor commit-msg guard forced Refs trailers; the noise ratchet caught 69 leaked diagnostics that two `--no-verify` merges had smuggled onto main; and the close used the new `goal-verdict --fields-file` and the new sprint-review coverage path.
- Parallel worktree delivery (EP0155, EP0150) plus serial build of the sprint.py-coupled cluster matched the coupling reality EP0154 itself detects - test files are coupling, so the sprint.py cluster stayed serial.

## What was hard / what stalled

- The MAJOR was a **selection-bias** hole in my own tests: US0400's test asserted only the rate LABEL (`rate_source`), never the value, so a design rung that still computed the full build-rate tokens passed green. The fix asserts the value; the lesson is the test, not the code.
- Two worktree agents committed with `--no-verify` for an environmental worktree-sweep failure (BG0271), which let their leaks bypass the noise ratchet - so the FIRST hook run over the merged tree failed on an inherited red ratchet, not on my own change. A `--no-verify` in one clone becomes someone else's red gate.
- US0392's grooming premise was wrong (telemetry takes no free prose); caught only when the code met reality. The story was corrected during delivery with recorded rationale.

## Lessons

- **A test that asserts a label, not the value, proves the tool named its state - not that it reached it.** US0400 relabelled the marginal rate UNMEASURED and still priced the build; the label-only test passed. Assert the number, not the tag.   <!-- record it: lessons add (project tier) -->
- **A `--no-verify` commit in a worktree defers the gate to whoever merges it.** Two agents' bypassed leaks became the first full-tree hook's red ratchet. A ratchet only holds if every writer runs it - so fix the environmental blocker (BG0271) rather than routing around it.
- **A library function that prints leaks into every test that calls it.** refine's SEEDED note printed from the library; 69 leaks. Return the notes, let the CLI layer report them.

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

| Unit | Points | Estimate (plan-time) | Actual | Ratio (est/actual) | Tokens/pt | Size | Wall | Model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US0371 | 5 | 244,555 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0391 | 3 | 146,733 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0392 | 3 | 146,733 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0393 | 2 | 97,822 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0398 | 5 | 244,555 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0399 | 3 | 146,733 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0400 | 3 | 146,733 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0401 | 2 | 97,822 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0402 | 5 | 244,555 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0403 | 2 | 97,822 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0404 | 5 | 244,555 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0405 | 2 | 97,822 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0406 | 2 | 97,822 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0407 | 5 | 244,555 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0408 | 2 | 97,822 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0409 | 2 | 97,822 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0410 | 5 | 244,555 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0411 | 3 | 146,733 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0412 | 2 | 97,822 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 19 unit(s) measured; 19 of 19 forecast at plan time.**

**Sprint tokens/point: 112,123** (6,839,526 tokens over 61 delivered points, harness-tracked). The token count is deterministic (supply it with `accuracy --tokens N`) - not UNMEASURED. A descriptive velocity, never a target.

**Velocity: 10.69 points/elapsed-hour** (61 points over 5.707h, run-state, ceremony included). This is the planning number - points per SESSION within the observed single-session envelope; it is NOT a linear per-point rate to extrapolate to a 1-point or 100-point sprint, and it is descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).
Unmeasured: US0371, US0391, US0392, US0393, US0398, US0399, US0400, US0401, US0402, US0403, US0404, US0405, US0406, US0407, US0408, US0409, US0410, US0411, US0412. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- This was an interactive sprint (no runner), so per-unit token telemetry was not captured; the run's harness-tracked share is captured at `sprint close --apply-signoff`. The forecast's headline change this sprint (the rung-aware marginal) is itself the calibration lesson: a design rung must not be priced as a build.

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
| Gate unrunnable inside a git worktree (forced `--no-verify` on both parallel agents) | BG0271 |
| retro accuracy misattributes a run's rung when an older retro is re-run after a new run opened | BG0272 |
| refine `inherit:subset` bypasses the parent-declares-none check and never validates the subset | BG0273 |
| artefact retitle write phase has no rollback if a reference file becomes unreadable mid-loop | BG0274 |
| Test asserting a label not a value (US0400) let the MAJOR through | declined: fixed in-sprint and captured as a lesson above; the practice, not a unit, is the fix |

<!-- file one with: scripts/file_finding.py · check with: scripts/retro.py dispose --id RETROxxxx -->

## Close loop (gated)

`gate --require-retro RETRO0069` (this retro's id, file form) fails until all four are true:

- [ ] this retro exists AND passes its content check - required sections, at least one real
      lesson, and every finding dispositioned (`retro.py validate --id RETRO0069`)
- [ ] its lessons are in the project store, not just in this file (`retro.py extract --id RETRO0069`)
- [ ] open lessons re-validated: each is closed, extended, or within its horizon (`lessons revalidate`)
- [ ] `retros/LESSONS-SUMMARY.md` regenerated from the still-valid lessons (`lessons summary`)

The next sprint reads them automatically: `sprint plan` prints the digest in the plan.

## Metrics

- Tokens: not-yet-captured (interactive; captured at close) · Duration: interactive session · Critic rejects: 0 at the unit level; the sprint-level adversarial panel returned 7 findings across the batch, all fixed before sign-off

## Handoff

- [HO-0023](../handoffs/HO0023-a-themed-batch-that-stops-eight-sprint-engine.md) - 19 remaining item(s): 11 copilot-tail, 8 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
