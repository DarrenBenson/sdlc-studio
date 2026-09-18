# US0833: sign writes the principal, the date and the report fingerprint against the run, and nothing else runs after it

> **Status:** Review
> **Delivers:** RFC0059
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Epic:** EP0255
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** sign writes the principal, the date and the report fingerprint against the run, and nothing else runs after it
**So that** RFC0059 is delivered by work that can be planned and checked

## Acceptance Criteria

This story carries BOTH halves of RFC0059's option E, because the consult found that the first
half alone is not a transaction: a signature nothing refuses to write over only ORDERS the work,
and ordering is a convention. So the seal is written here (AC1), the principal is judged by
`critic.py`'s own rule here (AC2), the post-seal write is refused here (AC3) and the re-open is
recorded here (AC4). US0845 is the READ side - what an already-broken seal looks like to a
reader - and nothing in that story refuses anything.

Two facts at HEAD the criteria rest on. `critic.record_signoff` (critic.py:2033) already refuses
a principal equal to the unit's author and a principal in `_session_reviewer_ids(repo_root,
unit)` - the authoring session's own subagents - but it is PER UNIT, and `sign` is run-level, so
the rule has to be applied across the batch rather than re-implemented; re-implementing it is
CR0571 returning in a new command. And `transition.transition` is the single chokepoint for a
status write: `artifact.close` routes through it (artifact.py:1342), so one refusal there covers
both routes.

D4 of RFC0059 is open, and AC3 pins the narrowest reading that can be re-derived: a write is
refused while the run is SEALED, judged by the run record's signature, never by comparing the
tree against a fingerprint - that comparison is US0845's, and it answers a different question.

THE SEALED RUN is US0832's prepared run carrying report RPT0001, signed by `sprint.py sign`,
whose batch is US0832's two stories and one bug, plus one story OUTSIDE the batch left at Ready
as the paired control.

### AC0: one principal, one act - SEAL writes the per-unit rows AND the run's signature

- **Given** THE PREPARED RUN, every unit's terminal gate clear and no unit yet moved
- **When** `sprint.py sign --report <id> --principal "Darren Benson"` runs once
- **Then** each batch unit gains its sign-off row naming that principal, reaches its terminal status, its parent epic and request cascade, and the run gains ONE run-level signature - all from the single principal the command was given, with no second prompt and no second command
- **Mutant:** write the run signature and leave the per-unit rows to a later `--apply-signoff` - the operator then signs twice for one decision, which is the shape D0213 rejected
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SealTests::test_one_principal_writes_the_unit_rows_and_the_run_signature
- **Verified:** yes (2026-09-18)

### AC1: sign records the principal, the date and the report's OWN fingerprint against the run

- **Given** US0832's prepared run carrying report RPT0001, whose JSON on disk holds fingerprint F
- **When** `sprint.py sign --report RPT0001 --principal "Darren Benson"` runs through `main`
- **Then** the run record's signature holds exactly the principal, an ISO date, the report id and F - F compared against the value read back from `RPT0001.json`, not against one the test computes; and the report's Markdown twin sign-off table carries those three and only those three, with no command line and no "unsigned" declaration in it
- **Mutant:** record the principal, the date and the report ID without the fingerprint - "signed RPT0001" then says nothing about WHICH RPT0001, and every re-prepare produces another one under the same id
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TheSealIsATransactionTests::test_sign_records_principal_date_and_the_reports_own_fingerprint
- **Verified:** yes (2026-09-18)

### AC2: sign refuses a principal the authoring session controls, by critic.py's rule over the whole batch

- **Given** US0832's prepared run where the SECOND batch unit alone carries a critic evidence row naming reviewer `Sam Eriksson (qa)`, and every unit's recorded author is `Claude Opus 5`
- **When** `sprint.py sign --report RPT0001 --principal "Sam Eriksson (qa)"` runs, and separately `--principal "Claude Opus 5"`
- **Then** both exit 2 carrying `critic.py`'s own refusal wording - the authoring-session-subagent refusal and the self-sign-off refusal - the run is left open and no signature is written; the subagent case must refuse although the reviewer is recorded on the second unit only, so a check that reads the first unit alone fails this criterion
- **Mutant:** judge the principal against the run's own author field alone - the subagent that reviewed every unit in the batch then signs the run off, which is CR0571 in a new command and the finding the consult raised against this story by name
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TheSealIsATransactionTests::test_sign_refuses_a_principal_the_authoring_session_controls
- **Verified:** yes (2026-09-18)

### AC3: a sealed run refuses the writes that would move its facts, naming the report and the way back

- **Given** THE SEALED RUN, and its bug unit at `Fixed`
- **When** `transition.py <the bug> --to "In Progress"` runs through `transition.main`, and separately the same transition on the story outside the batch
- **Then** the batch unit's transition exits non-zero, the unit file is byte-unchanged, and stderr names RPT0001, the sealed run id and the `sprint.py reopen` command; the unit outside the batch transitions as today, exit 0 - so the refusal is scoped to the sealed run's batch rather than to the repository
- **Mutant:** print the drift as a warning and let the write through - the seal is then ordering advice, which is the consult's finding in its own words, and every assertion about the message still passes
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::SealedRunRefusesWritesTests::test_a_sealed_runs_batch_unit_cannot_be_transitioned
- **Verified:** yes (2026-09-18)

### AC4: re-opening is explicit, carries a reason, and keeps the signature it breaks

- **Given** THE SEALED RUN
- **When** `sprint.py reopen --run <the run id> --reason "late repair to US0832"` runs, then AC3's refused transition is repeated; and separately `sprint.py reopen --run <the run id>` with no `--reason`
- **Then** a reopen of a run that was never sealed exits 2 naming that (the reason-less form is argparse's already, `sprint.py reopen` at 11638 declaring `--reason` required, so it proves nothing here) and writes nothing; the reasoned form exits 0, appends a re-open record carrying the run id, RPT0001, the reason and a date, and the repeated transition then succeeds; and the run record still holds the signature from AC1 beside the re-open record, so what was signed and when it was broken are both readable afterwards
- **Mutant:** clear the signature on re-open - the record then cannot say what had been signed, and US0845 has no signed fingerprint left to render INVALIDATED against
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TheSealIsATransactionTests::test_reopen_is_recorded_and_keeps_the_signature_it_breaks
- **Verified:** yes (2026-09-18)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC0 | write the run signature and leave the per-unit rows to a later `--apply-signoff` - the operator then signs twice for one decision, which is the shape D0213 rejected | one principal, one act - SEAL writes the per-unit rows AND the run's signature |
| AC1 | record the principal, the date and the report ID without the fingerprint - "signed RPT0001" then says nothing about WHICH RPT0001, and every re-prepare produces another one under the same id | sign records the principal, the date and the report's OWN fingerprint against the run |
| AC2 | judge the principal against the run's own author field alone - the subagent that reviewed every unit in the batch then signs the run off, which is CR0571 in a new command and the finding the consult raised against this story by name | sign refuses a principal the authoring session controls, by critic.py's rule over the whole batch |
| AC3 | print the drift as a warning and let the write through - the seal is then ordering advice, which is the consult's finding in its own words, and every assertion about the message still passes | a sealed run refuses the writes that would move its facts, naming the report and the way back |
| AC4 | clear the signature on re-open - the record then cannot say what had been signed, and US0845 has no signed fingerprint left to render INVALIDATED against | re-opening is explicit, carries a reason, and keeps the signature it breaks |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-17 | grooming 2026-09-17 | Groomed: four criteria, carrying BOTH halves of RFC0059's option E on the consult's finding that a signature nothing refuses over is a convention. Adds the CR0571 inheritance (critic.py's principal rule applied across the batch, the reviewer recorded on the SECOND unit only), the post-seal refusal at `transition.transition` (the chokepoint `artifact.close` routes through) and a recorded re-open that keeps the signature. Affects and Points grown for the two new files. |
| 2026-09-18 | goal review round 5 | AC4's reason-less arm withdrawn: `sprint.py reopen` at 11638 already declares `--reason` required, so that arm tested argparse rather than this story. It now proves the reopen of a run that was never sealed. |
| 2026-09-18 | delivery | `critic.signoff_refusal` extracted so the independence rule has one definition and two callers: `record_signoff` raises what it returns, and the seal asks it of every batch unit BEFORE writing. AC2 as written could not otherwise hold - a subagent recorded on the second unit alone was caught only after the first was signed and moved. AC4's re-open record gained the report id. Five mutants applied; AC0, AC1, AC2 and AC4 killed here, AC3 in `transition.py`. |
