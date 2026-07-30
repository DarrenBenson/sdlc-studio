# BG0451: start_batch fabricates a null-id run in a project with no run, and the next sprint plan then silently destroys the batch span it wrote

> **Status:** Open
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

## Acceptance Criteria

- [ ] The behaviour described is corrected: `run_state.start_batch`'s apply does `state = state or _blank()`, so opening a delivery batch in a project that has never opened a run MINTS a run state of...
- [ ] Following the recorded steps no longer reproduces the defect: Executed at d7a1ad8f, 2026-07-30, by an independent round-2 reviewer in an isolated worktree.
- [ ] The proposed fix lands, pinned by a test: Apply the guard that `note_finding` already carries: refuse to open a batch when no run is open, naming the absence, rather than seeding a blank state.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | independent round-2 reviewer (isolated worktree) | Filed |
