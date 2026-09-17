# US0832: close splits into PREPARE, which does everything that can change facts, and SEAL, which does not

> **Status:** Draft
> **Delivers:** RFC0059
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0255
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** close splits into PREPARE, which does everything that can change facts, and SEAL, which does not
**So that** RFC0059 is delivered by work that can be planned and checked

## Acceptance Criteria

The split is judged by what each half WRITES, never by what its help text claims. PREPARE is
`sprint.py close` under its existing name - the ten `_CLOSE_CHAIN` steps, the handoff re-render,
the velocity row and the final reconcile. It fans out NOTHING: under D0213 the run carries ONE
signature, so the per-unit sign-off rows, the terminal transitions and the parent epic and
request cascades all belong to SEAL, which applies them from the single principal it is given.
The consequence is stated here because it changes what the report says: at the moment the report
is produced no unit is terminal yet, so the report describes each unit as having CLEARED ITS
TERMINAL GATE, never as Done, and SEAL performs the transitions that make it so. SEAL is a new `sprint.py sign`, and its
whole job is the signature and the run's end. Two shapes at HEAD make the split falsifiable:
the chain's `handoff` step closes the run object (sprint.py:9572 re-reads the state for exactly
that reason), so PREPARE today ends the run before anything could sign it; and
`close --apply-signoff` runs the fan-out AND the tail, which is where RUN-01M2JA6J's two hours
of post-signature work came from. THE PREPARED RUN is a fixture run whose batch holds two
story units and one bug, every unit reviewed and answered, a recorded retro and a recorded
goal verdict, so PREPARE has no refusal to make and the criteria below judge ordering rather
than gating (US0834 owns the gating).

### AC1: PREPARE runs every step that can change a fact and leaves the run OPEN with a report to sign

- **Given** THE PREPARED RUN, open
- **When** `sprint.py close --retro RETRO0001` runs through `main` - PREPARE takes no principal, because it signs nothing
- **Then** it exits 0; every unit's terminal gate is recorded CLEAR and no unit has moved (`transition.requirements` returns no unmet requirement for each, and each unit's Status is unchanged on disk); `run_state.read(root)` still returns an OPEN run - no `closed_at`, no archived record under `.local/run-archive/` - carrying a `report` field naming an id whose JSON exists on disk; and the last line of stdout is the `sprint.py sign --report <id> --principal ...` command, named as the only action left
- **Mutant:** leave the `handoff` chain step closing the run object - the chain still runs, every unit still transitions, and the only thing that breaks is that SEAL has no open run to seal, which no assertion about the chain would catch
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PrepareAndSealTests::test_prepare_runs_every_fact_changing_step_and_leaves_the_run_open

### AC2: SEAL writes the signature and the run's end, and changes nothing else in the tree

- **Given** THE PREPARED RUN after AC1's PREPARE, with the bytes of every tracked path under the fixture root recorded
- **When** `sprint.py sign --report <the report id> --principal "Darren Benson"` runs through `main`
- **Then** it exits 0, the run is closed (`closed_at` set and `run_state.read_archived` returns the record), and the ONLY paths whose bytes differ from the recording are the run state, its archived copy and the report's own two files - no unit file, no `_index.md`, no retro, no `VELOCITY.md`, no handoff and no `reviews/` ledger
- **Mutant:** call `_apply_signoff_tail` from `sign` as `_apply_signoff` does today - the velocity row, the handoff re-render, the epic and request cascades and the reconcile then all run after the signature, which is RUN-01M2JA6J exactly, and every assertion about the signature itself still passes
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PrepareAndSealTests::test_seal_writes_the_signature_and_nothing_else_in_the_tree

### AC3: `close --apply-signoff` no longer signs, and names `sign` instead

- **Given** THE PREPARED RUN after AC1's PREPARE
- **When** `sprint.py close --retro RETRO0001 --apply-signoff --principal "Darren Benson"` runs through `main`
- **Then** it exits 2, stderr names `sprint.py sign` as the replacement, no row is appended to `sdlc-studio/reviews/signoff-record.md`, and the run is still open
- **Mutant:** keep `--apply-signoff` as an alias that calls `sign` - every operator, help file and runbook row keeps the old path, and the split ships with its own bypass intact (LL0027: gate it in the command people run)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PrepareAndSealTests::test_apply_signoff_is_refused_and_names_sign

### AC4: PREPARE is re-runnable after a late fix, and the second run re-derives rather than reuses

- **Given** THE PREPARED RUN after AC1's PREPARE, with one batch unit's file then edited so a figure the report carries moves (a criterion marked `- **Verified:** yes`, lifting the unit's verified-criteria count)
- **When** `sprint.py close --retro RETRO0001 --principal "Darren Benson"` runs a second time
- **Then** it exits 0; no unit is transitioned twice and `signoff-record.md` holds one row per unit, not two; `VELOCITY.md` holds one row for RETRO0001; and the report the run now names carries a DIFFERENT fingerprint from the first, with the moved figure at its new value
- **Mutant:** return the existing report when the run already names one - the late fix is then invisible and the operator signs a fingerprint over facts that have moved underneath it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PrepareAndSealTests::test_prepare_is_rerunnable_and_re_derives_the_report

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-17 | grooming 2026-09-17 | Groomed: four criteria. PREPARE is `close` (chain + fan-out + tail) and SEAL is a new `sign`; the split is judged by what each half WRITES, with a tree snapshot across `sign`. `--apply-signoff` is refused and names `sign`; a re-prepare re-derives the report. |
