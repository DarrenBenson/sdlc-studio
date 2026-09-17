# US0833: sign writes the principal, the date and the report fingerprint against the run, and nothing else runs after it

> **Status:** Draft
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

### AC1: sign records the principal, the date and the report's OWN fingerprint against the run

- **Given** US0832's prepared run carrying report RPT0001, whose JSON on disk holds fingerprint F
- **When** `sprint.py sign --report RPT0001 --principal "Darren Benson"` runs through `main`
- **Then** the run record's signature holds exactly the principal, an ISO date, the report id and F - F compared against the value read back from `RPT0001.json`, not against one the test computes; and the report's Markdown twin sign-off table carries those three and only those three, with no command line and no "unsigned" declaration in it
- **Mutant:** record the principal, the date and the report ID without the fingerprint - "signed RPT0001" then says nothing about WHICH RPT0001, and every re-prepare produces another one under the same id
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TheSealIsATransactionTests::test_sign_records_principal_date_and_the_reports_own_fingerprint

### AC2: sign refuses a principal the authoring session controls, by critic.py's rule over the whole batch

- **Given** US0832's prepared run where the SECOND batch unit alone carries a critic evidence row naming reviewer `Sam Eriksson (qa)`, and every unit's recorded author is `Claude Opus 5`
- **When** `sprint.py sign --report RPT0001 --principal "Sam Eriksson (qa)"` runs, and separately `--principal "Claude Opus 5"`
- **Then** both exit 2 carrying `critic.py`'s own refusal wording - the authoring-session-subagent refusal and the self-sign-off refusal - the run is left open and no signature is written; the subagent case must refuse although the reviewer is recorded on the second unit only, so a check that reads the first unit alone fails this criterion
- **Mutant:** judge the principal against the run's own author field alone - the subagent that reviewed every unit in the batch then signs the run off, which is CR0571 in a new command and the finding the consult raised against this story by name
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TheSealIsATransactionTests::test_sign_refuses_a_principal_the_authoring_session_controls

### AC3: a sealed run refuses the writes that would move its facts, naming the report and the way back

- **Given** THE SEALED RUN, and its bug unit at `Fixed`
- **When** `transition.py <the bug> --to "In Progress"` runs through `transition.main`, and separately the same transition on the story outside the batch
- **Then** the batch unit's transition exits non-zero, the unit file is byte-unchanged, and stderr names RPT0001, the sealed run id and the `sprint.py reopen` command; the unit outside the batch transitions as today, exit 0 - so the refusal is scoped to the sealed run's batch rather than to the repository
- **Mutant:** print the drift as a warning and let the write through - the seal is then ordering advice, which is the consult's finding in its own words, and every assertion about the message still passes
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::SealedRunRefusesWritesTests::test_a_sealed_runs_batch_unit_cannot_be_transitioned

### AC4: re-opening is explicit, carries a reason, and keeps the signature it breaks

- **Given** THE SEALED RUN
- **When** `sprint.py reopen --run <the run id> --reason "late repair to US0832"` runs, then AC3's refused transition is repeated; and separately `sprint.py reopen --run <the run id>` with no `--reason`
- **Then** the reason-less form exits 2 and writes nothing; the reasoned form exits 0, appends a re-open record carrying the run id, RPT0001, the reason and a date, and the repeated transition then succeeds; and the run record still holds the signature from AC1 beside the re-open record, so what was signed and when it was broken are both readable afterwards
- **Mutant:** clear the signature on re-open - the record then cannot say what had been signed, and US0845 has no signed fingerprint left to render INVALIDATED against
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TheSealIsATransactionTests::test_reopen_is_recorded_and_keeps_the_signature_it_breaks

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-17 | grooming 2026-09-17 | Groomed: four criteria, carrying BOTH halves of RFC0059's option E on the consult's finding that a signature nothing refuses over is a convention. Adds the CR0571 inheritance (critic.py's principal rule applied across the batch, the reviewer recorded on the SECOND unit only), the post-seal refusal at `transition.transition` (the chokepoint `artifact.close` routes through) and a recorded re-open that keeps the signature. Affects and Points grown for the two new files. |
