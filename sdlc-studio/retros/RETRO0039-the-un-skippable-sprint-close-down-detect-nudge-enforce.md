# RETRO-0039: The un-skippable sprint close-down: detect, nudge, enforce

> **Date:** 2026-07-16
> **Batch:** US0163, US0164, US0165, US0166 (EP0046, from RFC0042)
> **Goal:** done
> **Delivered:** 4 / 4   **Blocked:** 0

## Delivered

- **US0163 (5pt) - the close-owed detector.** `close_owed.py` answers "is a sprint close owed
  right now?" deterministically: a delivery unit (epic/story/bug) that reached terminal since a
  one-time grandfather **baseline** with no retro's `Batch` naming it. The baseline is the exact
  **set** of ids terminal at adoption (`.close-owed-baseline.json`), so a unit in flight at adoption
  that closes later is still held to a close, and non-numeric (ULID / v3) ids work.
- **US0164 (3pt) - the soft nudge.** `status`/`hint` carry an `advisory:` line when a close is owed,
  and a second nudge when close-owed tracking is uninitialised (terminal units, no baseline) - so
  neither the owed close nor its prerequisite is invisible.
- **US0165 (5pt) - the gate lane.** `gate --require-close` binds a blocking `close-owed` lane for
  the push/release moment. Bound-only (never in the plain gate), blocks on crash, deselect refused -
  the same discipline as the other close/release lanes.
- **US0166 (5pt) - the Stop hook + doctrine.** `hooks/close_guard.py` is an optional Claude Code Stop
  hook that reminds the agent of an owed close before a turn ends - default-allow on any doubt, never
  a hard-lock. The doctrine (`reference-retro.md`, `help/gate.md`) now states a sprint is complete
  only when the close gate is green, never at "deployed".

## Blocked / deferred

- Nothing blocked. This closes RFC0042 (Accepted by derivation - its only child EP0046 is Done).

## What went well

- **The feature caught its own sprint.** After the four stories reached Done, `close_owed detect`
  flagged EP0046 + US0163-0166 as owing a close - a live end-to-end proof, cleared only by this
  very retro naming them. The tool works because it worked on itself.
- **The bound-lane invariants held the design honest.** Trying to make `close-owed` a
  warn-by-default gate check tripped two existing invariant tests (a bound lane must not sit in the
  plain gate; must block on crash). They were right: the soft nudge belongs on status/hint, the gate
  carries only the blocking lane. The architecture pushed back and the design got cleaner.

## What was hard / what stalled

- **The independent review found a real BLOCKER in the baseline model.** The first implementation
  baselined a per-prefix **highest id**, on the assumption that id order tracks closure order. It
  does not: a lower-id unit in flight at adoption that closes later was silently grandfathered - the
  exact false "none owed" this sprint exists to kill - and the model broke entirely on non-numeric
  v3 ULID ids (empty baseline, everything owed forever). The fix was one idea: baseline the **set**
  of terminal ids, not a cutoff. The tests had passed only because they never exercised the failing
  window. A guard that is only tested on the cases it handles is not tested.
- **The Stop hook contract was ambiguous.** The Claude Code docs and a guide agent disagreed on
  whether `stop_hook_active` is exposed and whether exit-2 blocks. Resolved by writing the hook
  **defensively** - honour the field if present, rely on internal loop prevention if absent, block
  via the documented JSON form, default-allow on every error path - so it is correct under either
  reading rather than betting on one.

## Lessons

- A grandfather baseline for "work done before adoption" must be the **set** of ids that existed,
  not a highest-id/date cutoff. A cutoff assumes id (or time) order tracks the state being
  grandfathered; whenever items can cross the boundary in a different order than they were created
  (a low-id unit still in flight at adoption), the cutoff silently forgives real debt. It also
  couples the mechanism to numeric ids, breaking on ULID/opaque id schemes. Set membership has
  neither hole and costs a list.
- A test suite that passes is evidence only about the cases it runs. This sprint's detector passed
  its own tests while carrying a BLOCKER, because every test exercised the *higher-id-closed-later*
  path and none the *lower-id-in-flight* one - the blind spot and the defect coincided. When a
  feature grandfathers on a boundary, test an item on **both** sides AND one that crosses it.
- When an external contract is ambiguous (the Stop hook's `stop_hook_active` / exit codes), write to
  the intersection of the plausible readings and fail safe, rather than picking one and hoping. A
  hook that blocks a turn on its own uncertainty is worse than one that misses a reminder.

## Estimate vs actual

The plan forecast ~450,000 tokens (18 points x the ~25,000 seed). The token actual is
harness-tracked (deterministic), not unmeasurable; this interactive sprint recorded no per-unit
telemetry, so the sprint total is **not-yet-captured** here - supply it with
`retro.py accuracy --id RETRO0039 --tokens N --write` to record a real tokens-per-point over the 18
delivered points (the capability US0161 shipped last sprint). Not-yet-captured, not unknowable.

<!-- accuracy:begin (generated by retro.py accuracy --write) -->
<!-- accuracy:end -->

- Descriptive only, never a target (CR0273): the figure informs the next plan's seed, it does not
  become a quota.

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the issues found?**

| Finding | Disposition |
| --- | --- |
| Baseline was a per-prefix highest-id cutoff -> silently grandfathered a lower-id unit that closes later, and broke on ULID ids (found in review) | declined: no ticket - fixed this sprint (baseline is now the set of terminal ids) + two regression tests (in-flight-lower-id + ULID). |
| Unbaselined state was silent and un-nudged -> the "un-skippable" close-down had a skippable, invisible prerequisite (found in review) | declined: no ticket - fixed this sprint (`status`/`hint` nudge to stamp a baseline when terminal units exist without one). |
| The default-allow hook test and US0165 deselect claim were not actually exercised (found in review) | declined: no ticket - fixed this sprint (a real `decide({})` test + `require_close` added to the gate deselect-refusal MODES). |
| `gate --require-close` returns PASS ("no baseline stamped yet") on an unbaselined project rather than failing closed | declined: acceptable - `--require-close` is opt-in, and the status/hint nudge carries discoverability; failing closed would surprise a first adopter. Revisit if it bites. |
| DoR/DoD as editable per-project artefacts (RFC0043) subsumes this close clause | deferred: RFC0043 filed and Accepted-pending; this sprint delivers the sprint-DoD's close clause it depends on. |

<!-- file one with: scripts/file_finding.py -->

## Close loop (gated)

- [x] this retro exists AND passes its content check
- [x] its lessons are in the project store
- [x] open lessons re-validated
- [x] `retros/LESSONS-SUMMARY.md` regenerated

## Metrics

- Tokens: not-yet-captured (harness-tracked; supply with `accuracy --tokens N`) · Duration: one session · Critic rejects: 1 (REQUEST-CHANGES first pass - a real BLOCKER in the baseline model + 1 MAJOR + 4 MINOR/NIT; all fixed, re-review requested)
