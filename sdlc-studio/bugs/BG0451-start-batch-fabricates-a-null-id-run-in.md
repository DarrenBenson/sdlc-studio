# BG0451: start_batch fabricates a null-id run in a project with no run, and the next sprint plan then silently destroys the batch span it wrote

> **Status:** Fixed
> **Severity:** Critical
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** independent round-2 reviewer (isolated worktree); agent; v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

`run_state.start_batch`'s apply does `state = state or _blank()`, so opening a delivery batch in a project that has never opened a run MINTS a run state of `{run_id: null, started_at: null, outcome: running}`. This is the same fabrication that was rated STOP-SHIP against `note_finding` in the previous review round; that repair guarded `note_finding` and left the sibling writer added in the same commit, which is also the DOCUMENTED FIRST COMMAND of the batch workflow. The consequence compounds: `_is_spent` treats a null `run_id` as spent, so the next `open_run` - that is, `sprint plan --write` - replaces the state with a fresh blank and takes the span with it. The batch span is destroyed with no warning, and every finding filed against it keeps a `Raised-in-batch` key pointing at a span that no longer exists, counted in neither placement number.

## Steps to Reproduce

Executed at d7a1ad8f, 2026-07-30, by an independent round-2 reviewer in an isolated worktree.

Fabrication, in a project with no run:

```text
read()                                          ->  {}
sprint.py review-batch --open US0001,US0002
read()  ->  {'`run_id`': None, '`started_at`': None, 'outcome': 'running'}
```

Destruction, on the next plan:

```text
spans before `open_run`:  [['US0001','US0002']]
spans after  `open_run`:  []
`open_batch`:             None
```

The reviewer rated the earlier `note_finding` instance of this fabrication a STOP-SHIP on the grounds that it breaks `read`'s documented never-fabricated invariant and lets `sprint close` proceed against a phantom running run with a null id. All of that holds here, plus the silent span loss.

## Proposed Fix

Apply the guard that `note_finding` already carries: refuse to open a batch when no run is open, naming the absence, rather than seeding a blank state. A batch is scoped to a run by definition, so opening one without a run is not a state to be minted but a command to be refused.

The deeper issue is worth settling in the same slice: `_mutate` persists whatever `apply` returns, so ANY writer that defaults a missing state to `_blank()` mints a phantom run. That is now two instances of one shape found in two consecutive review rounds, and the second was introduced by the commit that repaired the first. Either `_mutate` should refuse to persist a state the caller invented, or every writer needs the guard - and the first is one change while the second is a rule somebody has to remember.

Pin BOTH halves. A test that `start_batch` refuses with no run, and a test that an existing span SURVIVES a subsequent `open_run` - the second is the one that catches the data loss, and no test currently covers it.

> **Verification depth:** functional - both halves executed directly against the library and the fabrication reproduced before the fix. Two mutants KILLED (a straight revert, and the refusal message stripped, which proves the test asserts WHY rather than merely that it raised). The shared fixture was itself encoding the buggy contract - it started batches against no run - so it was corrected, which is why the guard had nothing to fail against before.

## Acceptance Criteria

### AC1: starting a batch with no run open is refused, and nothing is written

- **Given** a project that has never opened a run
- **When** `start_batch` is called
- **Then** it refuses naming the reason, and `read` still returns {} - both halves asserted, because a guard that raises AFTER writing would pass a test checking only the exception; the previous behaviour minted a run whose id was null, breaking read's documented never-fabricated invariant
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::DeliveryBatchSpanTests::test_starting_a_batch_with_no_run_open_is_REFUSED_and_writes_nothing
- **Verified:** yes (2026-07-30)

### AC2: a batch span survives the next plan of the same run

- **Given** an open run carrying a batch span
- **When** the run is re-planned
- **Then** the span is unchanged - this was the data-loss half and no test covered it: `_is_spent` read the null id as spent, so the next `sprint plan --write` replaced the state and took the span with it, leaving every finding's `Raised-in-batch` key pointing at nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::DeliveryBatchSpanTests::test_a_span_SURVIVES_the_next_plan_of_the_same_run
- **Verified:** yes (2026-07-30)

### AC3: the sibling guard on note_finding still holds, proven on its own runless fixture

- **Given** a project with no run, built by the test itself rather than inherited
- **When** a finding is attributed
- **Then** it returns None and writes no file - the shared fixture now opens a run, so this test builds its own; the two guards are siblings and the second was introduced by the commit that repaired the first
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::DeliveryBatchSpanTests::test_note_finding_never_fabricates_a_run
- **Verified:** yes (2026-07-30)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | independent round-2 reviewer (isolated worktree) | Filed |
