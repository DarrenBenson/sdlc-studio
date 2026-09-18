# US0832: close splits into PREPARE, which does everything that can change facts, and SEAL, which does not

> **Status:** Review
> **Delivers:** RFC0059
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0255
> **Points:** 8
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
- **Verified:** yes (2026-09-18)

### AC2: SEAL writes the signature and only what the signature entails

- **Given** THE PREPARED RUN after AC1's PREPARE, with the bytes of every tracked path under the fixture root recorded, and a `closed_at` marker absent
- **When** `sprint.py sign --report <the report id> --principal "Darren Benson"` runs through `main`
- **Then** it exits 0 and every path whose bytes differ is one the SIGNATURE entails: the run state and its archived copy, the report's own two files, the sign-off record, each batch unit's Status line and its index row, the handoff the run names, the velocity row, and the parent epic and request whose children are now resolved. Nothing else differs, and in particular SEAL does not run the close TAIL (`_apply_signoff_tail`): no gate re-run, no retro edit, no changelog, no final reconcile. The velocity row and the handoff ARE written, by `_cascade_after_signature` and not by the tail, because both are consequences of the transitions the signature just made - the velocity row counts DELIVERED units by status, which exist only because of it, and the handoff describes those statuses and would otherwise permanently describe the world one moment before the signature. D0213 puts the fan-out in SEAL and its consequences with it; what it does not put there is the tail
- **Mutant:** call `_apply_signoff_tail` from `sign` as `_apply_signoff` does today - the velocity row, the handoff re-render and the final reconcile then run after the signature, which is the two hours RUN-01M2JA6J spent after the operator had already said yes
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PrepareAndSealTests::test_seal_writes_the_signature_and_only_what_it_entails
- **Verified:** yes (2026-09-18)

### AC3: `close --apply-signoff` no longer signs, and names `sign` instead

- **Given** THE PREPARED RUN after AC1's PREPARE
- **When** `sprint.py close --retro RETRO0001 --apply-signoff --principal "Darren Benson"` runs through `main`
- **Then** it exits 2, stderr names `sprint.py sign` as the replacement, no row is appended to `sdlc-studio/reviews/signoff-record.md`, and the run is still open
- **Mutant:** keep `--apply-signoff` as an alias that calls `sign` - every operator, help file and runbook row keeps the old path, and the split ships with its own bypass intact (LL0027: gate it in the command people run)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PrepareAndSealTests::test_apply_signoff_is_refused_and_names_sign
- **Verified:** yes (2026-09-18)

### AC4: PREPARE is re-runnable after a late fix, and the second run re-derives rather than reuses

- **Given** THE PREPARED RUN after AC1's PREPARE, with one batch unit's file then edited so a figure the report carries moves - its `Points:` value, which feeds the delivered total and the per-point rate
- **When** `sprint.py close --retro RETRO0001` runs a second time, still with no principal
- **Then** it exits 0; no unit is transitioned twice and `signoff-record.md` is untouched by the re-run - the per-unit rows belong to SEAL, which has not run; and the report the run now names carries a DIFFERENT fingerprint from the first, with the moved figure at its new value in the re-derived page
- **Mutant:** return the existing report when the run already names one - the late fix is then invisible and the operator signs a fingerprint over facts that have moved underneath it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PrepareAndSealTests::test_prepare_is_rerunnable_and_re_derives_the_report
- **Verified:** yes (2026-09-18)

### AC5: PREPARE prints no second account of the run

- **Given** a prepared run, and the TWO legacy accounts `cmd_close` prints on its success path: `_draw_report` (defined sprint.py:7077, called 9603), whose body is `print(sprint_report.render(sprint_report.report(root, retro_id)))`, and `_tell_the_operator` (defined 6991, called 9610), which prints shipped and carried per unit with a cost block from `_close_cost`
- **When** `sprint.py close --retro RETRO0001` runs through `main`
- **Then** stdout carries exactly ONE set of delivered and cost figures, the filed report's, and `_draw_report` is no longer reached from `cmd_close` - grep of the close path finds no call, and neither `_draw_report` nor `_tell_the_operator` is reached from `cmd_close` - `sprint_report.report`, `sprint_report.render` and `sprint_report.close_report` are not invoked to render a page beside the one being filed
- **Mutant:** leave `_draw_report` in place - the operator then decides over two accounts of the same run, derived from two different root objects, which is the disagreement US0835 AC2's fixture was built to expose and the reason the goal's first word is ONE
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PrepareAndSealTests::test_prepare_prints_exactly_one_account_of_the_run
- **Verified:** yes (2026-09-18)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | `sprint.py _close_handoff`: restore `--outcome` to the handoff chain step, so PREPARE ends the run - the chain still runs and every unit still transitions, and the only break is that SEAL has no open run to seal | PREPARE runs every step that can change a fact and leaves the run OPEN with a report to sign |
| AC2 | `sprint.py cmd_sign`: pass `tail=True` to `_apply_signoff`, so the velocity row, the handoff re-render and the final reconcile run AFTER the signature | SEAL writes the signature and only what the signature entails |
| AC3 | `sprint.py cmd_close`: keep `--apply-signoff` as an alias that calls `sign`, so the old path survives in every operator's fingers, help file and runbook row | `close --apply-signoff` no longer signs, and names `sign` instead |
| AC4 | `sprint.py _file_the_report`: return the report the run already names instead of re-deriving it, so a late fix between two prepares is invisible and the operator signs over facts that have moved | PREPARE is re-runnable after a late fix, and the second run re-derives rather than reuses |
| AC5 | `sprint.py cmd_close`: restore the `_draw_report` and `_tell_the_operator` calls, so the close prints two further accounts of the run beside the page being signed | PREPARE prints no second account of the run |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-17 | grooming 2026-09-17 | Groomed: four criteria. PREPARE is `close` (chain + fan-out + tail) and SEAL is a new `sign`; the split is judged by what each half WRITES, with a tree snapshot across `sign`. `--apply-signoff` is refused and names `sign`; a re-prepare re-derives the report. |
| 2026-09-18 | goal review confirmation | AC5 added and raised 5 -> 8 points: the close prints TWO legacy accounts, not one - `_draw_report` at 9603 and `_tell_the_operator` at 9610 - and retiring both is the work the goal's first word requires. |
| 2026-09-18 | delivery | AC2's allowed set gains the handoff and the velocity row, with the reason: both are computed FROM unit statuses, and under D0213 those statuses exist only because the signature wrote them. Filing either at PREPARE would describe the world one moment before the signature, or count zero delivered. The tail itself still runs in PREPARE, so AC2's named mutant - calling `_apply_signoff_tail` from `sign` - is unchanged and still killed by the reconcile it would drag after the signature. |
| 2026-09-18 | plan review round 1 | AC2's Then contradicted itself and the code: it listed the velocity row and the handoff among what SEAL may write, then forbade a velocity recompute and a handoff re-render in the same sentence. `_cascade_after_signature` writes both, and must - they are consequences of the transitions the signature makes. The clause now separates the CASCADE (SEAL's, because the signature causes it) from the TAIL (PREPARE's, because it changes facts the report states), which is the distinction D0213 actually draws. |
| 2026-09-18 | plan review round 1 | AC4's Then carried a clause that is FALSE of its own Given: `VELOCITY.md` holds one row for RETRO0001. The fixture never creates that file at all - `retro accuracy` refuses an unmeasured sprint - so an assertion written to the criterion's words would have failed. Withdrawn rather than asserted. The Given also named a `Verified:` edit that moves no figure the report carries; it now names `Points:`, which does. The three remaining clauses are each asserted. |
