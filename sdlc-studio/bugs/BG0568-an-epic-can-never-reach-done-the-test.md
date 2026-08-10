# BG0568: an epic can never reach Done - the test-plan gate holds a container whose completion is derived, and nothing else checks its breakdown

> **Status:** Fixed
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/reference-scripts-create.md
> **Evidence:** Hit at the close of RUN-01KZM49Y, 2026-08-10, with every story terminal and signed off. `transition.py set --id EP0213 --status Done` refuses: `EP0213 has no ## Test Plan, and review.test_plan_after puts it in scope`. `--force` does not clear it - the gate is not forceable. The remedy it names then refuses too: `verify_ac.py testplan derive --unit EP0213` reports `the plan would carry 0 row(s) for 4 criterion/criteria`, because `refine apply` writes an epic's acceptance criteria as bare `- [ ]` items and the deriver reads `### ACn`. `reconcile detect` reports both epics as `epic-status-stale`, so the delivery backlog reads as larger than it is with no way to correct it.
> **Verification depth:** functional (unit: the gate driven through `transition.py set` from both entries, over all four breakdown states, for six artefact types, and with `--force`; mutation: seven planned mutants plus the reviewer's own vacuity probe applied and killed on the final tree; live: EP0213 and EP0214, the two epics this bug was filed from, closed through the shipped CLI and `reconcile detect` went to zero drift)
> **Created:** 2026-08-10
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Three shipped behaviours meet and leave no exit.

The test-plan gate fires on EVERY type - deliberately, because a bug's test plan is a test plan. An EPIC ships no code. Its stories carry the criteria, the test plans, the reviews and the sign-offs; the epic is a container whose completion is derived from theirs. Asking it to name the production change its own test must fail on has no honest answer, and inventing one would be exactly the manufactured paperwork the gate exists to prevent.

The gate is not forceable, which is right for a story and wrong here - `--force` clears the two-role bar and the AC-verify bar but not this one, so the one gate with no honest answer is the one with no override.

And the remedy it names cannot run. `refine apply` writes epic criteria as `- [ ]` checkbox items; `testplan derive` slices `### ACn`. The two shipped commands disagree about the shape of the artefact one of them wrote. That half is BG0545's class, but it matters here because it removes the only exit the refusal offers.

The result is that every epic minted by `refine` is permanently un-closable, and `reconcile` reports it as stale for ever.

## Steps to Reproduce

1. `refine apply` a request into an epic with stories. 2. Take every story to Done with reviews and sign-off. 3. `transition.py set --id <epic> --status Done` - refused for a missing Test Plan. 4. Add `--force` - still refused. 5. Run the `testplan derive` it names - refused, 0 rows for N criteria. 6. `reconcile detect` now reports `epic-status-stale` with no way to clear it.

## Proposed Fix

Scope the test-plan gate to units that CARRY code - stories and bugs - and let a container derive its completion from its breakdown, which is what `reconcile` already computes. An epic whose every declared unit is terminal and signed off has more evidence behind it than a test plan would add. If the gate must stay universal, then make it forceable on a container with a recorded reason, on the same terms as the two-role bar. Separately, `refine apply` and `testplan derive` must agree on the criterion shape - one of them writes what the other cannot read. Pin the exit: an epic whose stories are all terminal reaches Done through the shipped CLI, and one whose stories are not still refuses.

## Acceptance Criteria

> **Plan rewritten twice. Round 1 rejected five findings; round 2 rejected four more, each
> measured on a fixture with a working implementation applied.** The rulings that shaped this
> version:
>
> **Ruling 1 - the exit cannot rest on "an epic ships no code".** Five of 214 epics here carry an
> `Affects`. The honest rule is that an epic's completion is DERIVED from its breakdown, so the
> exit must CHECK the derivation rather than assume it.
>
> **Ruling 2 - a type-scope fix alone opens a hole, so this unit swaps one gate for the right
> one.** A seat applied the scope patch and closed a fixture epic whose only child was `Draft`, at
> exit 0: `_request_terminal_gate` is discovery-only, so an epic has no breakdown check at all.
>
> **Ruling 3 - the new gate is NOT entry-triggered.** The test-plan gate is guarded by
> `from_canon not in _IMPL_TARGETS`, and `In Progress` is in an epic's own vocabulary - a seat
> measured `In Progress -> Done` over a `Draft` child closing at exit 0 under the first
> implementation. The new gate fires on every transition INTO a terminal epic status.
>
> **Ruling 4 - the reader is `reconcile.declared_breakdown_ids`, named rather than implied.**
> `sdlc_md.children_of` enumerates by back-link and `declared_breakdown_ids` reads the Story
> Breakdown table; over this corpus they disagree on 10 of 214 epics. The gate must read what the
> DRIFT DETECTOR reads, or the ladder and the census disagree - which is this bug's own class.
>
> **Ruling 5 - the gate mirrors `epic_status_stale_drift`'s three documented silences, and is
> FORCEABLE.** That function's docstring already states the contract: it is detect-only "because
> closing an epic is a status transition and `transition.py set` is where an epic's own gates
> live". This gate is that missing counterpart. Being forceable is the point: an unforceable gate
> with no honest answer is the defect being fixed, and it must not be reintroduced.
>
> The BG0545 criterion-shape residue survives and is recorded here rather than promised.

### AC1

- **Given** a project that SETS `review.test_plan_after`, and an epic created on or after it
  carrying NO `## Test Plan` - all three pinned, because `_plan_gate_active` returns False without
  them and the mutant would then survive on a fixture that never armed the gate it restores - at
  `Draft`, a from-status deliberately OUTSIDE `In Progress`, `Review` and `Done`, every declared
  breakdown unit of which resolves and is terminal
- **When** `transition.py set --id <epic> --status Done` is run through the shipped CLI
- **Then** it succeeds, with no hand-written test plan and no `--force`.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k an_epic_with_a_terminal_breakdown_closes
- **Verified:** yes (2026-08-10)
- **Mutant:** in `transition.py`, revert the type-scope condition so `epic` is back inside the test-plan gate.

### AC2

- **Given** an epic whose breakdown holds one unit that is neither terminal nor `Deferred`
- **When** the transition is attempted BOTH from `Draft` and from `In Progress`
- **Then** it is REFUSED in both cases and the refusal NAMES the unfinished unit. The
  `In Progress` half is the load-bearing one: the gate this sits beside is entry-triggered, and a
  criterion asserting only the `Draft` path would pass while the live route stayed open.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k an_epic_over_unfinished_work_is_refused_from_every_entry
- **Verified:** yes (2026-08-10)
- **Mutant:** in `transition.py`, guard the new gate with `from_canon not in _IMPL_TARGETS` as its neighbour is.

### AC3

- **Given** the three states `epic_status_stale_drift` is documented as silent in - an empty or
  id-less breakdown, a declared id resolving to no file, and a `Deferred` child
- **When** each is transitioned
- **Then** the empty breakdown and the `Deferred` child CLOSE, matching the detector's exemptions,
  and the unresolvable id is REFUSED and named, because the detector records it as UNKNOWN rather
  than finished and an epic must not close over a child nothing can confirm. All three are
  `--force`-able, so no epic is ever permanently un-closable - which is the defect this unit
  exists to remove.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k the_epic_gate_mirrors_the_drift_detectors_silences
- **Verified:** yes (2026-08-10)
- **Mutant:** in `transition.py`, treat a `Deferred` child as blocking, which recreates the permanently-stuck epic.

### AC4

- **Given** a STORY and a BUG each entering `In Progress` past the cutoff with no approved test
  plan, and the four other types the gate holds today - `cr`, `plan`, `test-spec`, `workflow`
- **When** each is transitioned into the gate's target set
- **Then** every one is still REFUSED. `In Progress` is named deliberately for the bug: routed to
  `Fixed` it never reaches this gate at all. And the four other types make `type_ != "epic"`
  distinguishable from `type_ in ("story", "bug")`, which would silently release them.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k only_the_epic_is_released_from_the_test_plan_gate
- **Verified:** yes (2026-08-10)
- **Mutant:** in `transition.py`, replace the epic exclusion with a scope of story and bug.

### AC6

- **Given** the epic from AC2, refused over its unfinished child
- **When** the same transition is run with `--force`
- **Then** it SUCCEEDS, and the bypass is RECORDED - a `Forced-override` field and a Revision
  History row naming the waived gate. Without this row an implementation omitting `not force`
  passes every other criterion while reproducing this bug's headline symptom in a brand-new gate:
  the one gate with no override. Force is only worth having because `_force_bypassed` re-runs the
  ladder with force off and stamps what it waived, so the gate must sit INSIDE `_pre_write_gates`
  shaped `if not force and ...`; an early `if force: return None` loses the record and leaves
  theatre.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k a_forced_epic_close_succeeds_and_is_recorded
- **Verified:** yes (2026-08-10)
- **Mutant:** in `transition.py`, drop the `not force` guard from the epic gate so the bypass is unavailable.

### AC5

- **Given** an epic on which `reconcile.declared_breakdown_ids` and `sdlc_md.children_of` disagree
  - the table declaring one set and the back-links another, which is true of 10 of this corpus's
  214 epics
- **When** the gate evaluates it
- **Then** the CLI OUTCOME follows `declared_breakdown_ids`: an epic whose declared table is
  wholly terminal but which carries an extra `Draft` child by back-link CLOSES at exit 0. The Then
  is an exit code, not a claim about which function was called - a criterion asserting the latter
  is satisfiable by a monkeypatch and by a fixture where the two readers disagree on membership
  while agreeing on verdict, and the mutant survives both.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k the_gate_and_the_drift_detector_read_one_breakdown
- **Verified:** yes (2026-08-10)
- **Mutant:** in `transition.py`, switch the gate to `sdlc_md.children_of`.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `transition.py`, revert the type-scope condition so `epic` is back inside the test-plan gate | |
| AC2 | in `transition.py`, set the new epic gate's entry condition to `from_canon not in _IMPL_TARGETS`, as its neighbour has | |
| AC3 | in `transition.py`, change the epic gate to treat a `Deferred` child as blocking; and separately, change it to close over an unresolvable declared id | |
| AC4 | in `transition.py`, replace the epic exclusion with a scope of story and bug | |
| AC6 | in `transition.py`, delete the `not force` guard from the epic gate so the bypass is unavailable | |
| AC5 | in `transition.py`, change the epic gate's breakdown reader to `sdlc_md.children_of` | |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-10 | sdlc-studio | Filed |
