# US0286: The three heavy gate lanes share one artefact corpus instead of walking it each

> **Status:** Draft
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py,.claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Depends on:** US0284
> **Epic:** EP0093
> **Points:** 5
> **Persona:** repo maintainer (dogfooding operator)

## User Story

**As a** repo maintainer running the gate on every commit
**I want** the gate to read the artefact corpus once per run instead of once per lane
**So that** the 35.6 seconds every commit pays is spent reading the tree once, not three times

## Context

Measured 2026-07-21, `run_gate` costs 35.6s across 15 lanes, and three of them are 83% of it:
engagement-floor 11.0s, constitution 10.2s, validate 8.2s. Each walks and parses the same
~1,800-artefact corpus independently.

This is the only story in the epic that touches product code, and it is the highest-value one,
because the cost is not confined to the suite: the pre-commit hook pays this on every single
commit, and the close pays it again. The saving therefore lands three times over.

The hazard is precise and worth naming: a corpus cache that outlives its run would let the gate
pass on a tree it never read. Fail-open staleness is the same class as the vacuity defects this
project keeps finding, so the cache is per-run and in-memory only, and AC2 and AC5 exist to
attack that specific failure rather than the happy path.

## Acceptance Criteria

### AC1: the corpus is parsed once per run

- **Given** a gate run over a tree of artefacts
- **When** the lanes that need the corpus execute
- **Then** the corpus has been walked and parsed exactly once, and each lane read that one copy
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::CorpusSharingTests::test_the_corpus_is_parsed_once_per_run

### AC2: the cache never outlives its run

- **Given** a completed gate run, and an artefact edited afterwards
- **When** a second run executes in the same process
- **Then** it re-reads the tree and sees the edit, so no run can report on a tree it did not read
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::CorpusSharingTests::test_a_second_run_rereads_the_tree

### AC3: every lane reports what it reported before

- **Given** the same tree, before and after the change
- **When** all 15 lanes run
- **Then** each reports the same count, status and blocking flag as it did before
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py

### AC4: sharing did not narrow what any lane reads

- **Given** a change visible only to one lane
- **When** that lane runs against the shared corpus
- **Then** it still detects the change, so the shared corpus is not a lowest-common-denominator
  subset of what the lanes used to read for themselves
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::CorpusSharingTests::test_sharing_does_not_narrow_a_lane

### AC5: the staleness hazard is mutation-checked

- **Given** the corpus path in `gate.py`
- **When** mutants are applied to it
- **Then** the new tests kill them, in particular any mutant that would let a cached corpus
  survive into a second run
- **Verify:** manual run mutation.py scoped to the corpus functions and record the kills before
  the change is accepted. A caching bug that returns stale data is exactly the class a green
  suite hides.
- **Verified:** manual

### AC6: the saving is measured, not assumed

- **Given** the 35.6s baseline and per-lane split measured on 2026-07-21
- **When** the change is delivered
- **Then** the measured time and the new per-lane split are recorded against it
- **Verify:** manual record the measured time and per-lane split at delivery; a standing
  threshold is machine-dependent.
- **Verified:** manual

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Created via `new` (deterministic) |
