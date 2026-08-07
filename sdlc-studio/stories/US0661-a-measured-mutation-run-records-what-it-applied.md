# US0661: A measured mutation run records what it applied, attributed to a unit, so the gate is satisfiable by measurement rather than only by self-report

> **Status:** Review
> **Delivers:** CR0537
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Epic:** EP0212
> **Depends on:** BG0541
> **Points:** 8
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A measured mutation run records what it applied, attributed to a unit, so the gate is satisfiable by measurement rather than only by self-report
**So that** CR0537 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: a measured run satisfies the gate, and its absence still refuses

- **Given** a pair of fixtures under `review.mutation_evidence: block`, identical but for one
  thing: a repair whose only evidence is a real `mutation.py run` over its changed lines with
  every mutant killed and no `register` claim at all, and the same repair with those per-mutant
  records removed
- **When** `transition.py set --id BG0001 --status Fixed` runs on each
- **Then** the first exits 0 and the second is REFUSED. The pair is the criterion: today
  `append_ledger` writes a summary counter block per target and no `mutants` list, and the gate
  selects on `mutants[].unit`, so the strongest evidence available reads as NO evidence and only
  the author's own typed claim opens the gate. Asserting exit 0 alone is vacuous, because
  `transition.py set` exits 0 for every ledger until BG0541 wires the lane
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::MeasuredEvidenceCLITests::test_a_measured_run_satisfies_the_gate
- **Verified:** yes (2026-08-07)

### AC2: a measured record is attributed to the unit that caused it

- **Given** ONE real `mutation.py run` attributed to a unit, and beside it that same ledger with
  only the `unit` key stripped, under `review.mutation_evidence: block`. The positive half is a
  produced ledger rather than a hand-authored one, because a hand-authored positive leaves the
  row's mutant lethal only through AC3
- **When** `transition.py set --id BG0001 --status Fixed` runs on each
- **Then** the first exits 0 and the second is REFUSED. Persisting the list is half the change:
  `enumerate_mutations` yields `{file, class, occurrence, line}` with no unit and `mutation.py run`
  takes no `--unit`, so a plan that pins only persistence leaves the attribution unpinned and the
  gate shut for a second reason nobody measured. The pair is the criterion because a refusal
  alone is not discriminating - an unattributed record and an absent one both leave the gate's
  selection empty and produce the identical message, so no single fixture can tell them apart
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::MeasuredEvidenceCLITests::test_a_measured_record_is_attributed_to_its_unit
- **Verified:** yes (2026-08-07)

### AC3: the ledger records the shape the gate selects on

- **Given** a completed `mutation.py run` attributed to a unit
- **When** the ledger entry it appends is read back
- **Then** each per-mutant record carries the file, the line, the applied mutation, the verdict
  and the unit - the fields the gate selects and the refusal quotes. This is the record-shape half,
  asserted where the record is written rather than through the gate, so a failure says which of
  the two halves broke
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::MeasuredAttributionTests::test_a_measured_entry_records_the_shape_the_gate_selects_on
- **Verified:** yes (2026-08-07)

### AC4: a ledger that contradicts itself refuses in every mode, `off` included

- **Given** a mutant registered `killed` at a file and line, and a measured run recording
  `survived` at that same file and line under the same content hash, with
  `review.mutation_evidence: off`; and beside it the control, a mutant registered `killed` and
  measured `killed` at the same target, line and hash
- **When** the terminal transition runs on each
- **Then** the first REFUSES, naming both records and the fact that they contradict, and the
  second PROCEEDS under both `off` and `block`. This is not a quality bar being applied under
  `off`, it is the instrument lying about itself, and every figure derived from a false verdict is
  wrong. The control is named because a check that refuses on any co-located pair passes the
  refusal test for the wrong reason
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::MeasuredEvidenceCLITests::test_a_recorded_kill_shown_to_survive_refuses_even_when_off
- **Verified:** yes (2026-08-07)

### AC5: a registered mutant records a line, and a missing line is refused not defaulted

- **Given** `mutation.py register --unit BG0001 --target src/thing.py --line 2 --verdict survived`,
  and beside it the same command with `--line` omitted
- **When** the ledger is read back
- **Then** the first record carries the line and the second is REFUSED at registration, because
  the verdict is non-equivalent. Today no shipped verb can record a line, so every test asserting
  one passes on a fixture the tool itself could never produce. And an optional line is worse than
  none: a registered `line: None` never joins a measured `line: 2`, so AC4's contradiction check
  silently never fires while its own fixture, which always supplies a line, stays green
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::RegisteredLineTests::test_register_records_a_line_and_refuses_a_missing_one
- **Verified:** yes (2026-08-07)

### AC6: the refusal quotes the line rather than a question mark

- **Given** the ledger AC4 produced, under `review.mutation_evidence: block`
- **When** the terminal transition is refused
- **Then** the SURVIVOR listing quotes `src/thing.py:2`, not `src/thing.py:?`. The refusal is
  named because the AC5 ledger can fire either that listing or AC4's contradiction check, and a
  mutant is lethal only to whichever returns first. The clause is verified here
  rather than under AC5 because the string is composed in `transition.py`, and an assertion about
  a refusal placed in `test_mutation.py` is a claim tested where it is not made
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::MeasuredEvidenceCLITests::test_the_refusal_quotes_the_registered_line
- **Verified:** yes (2026-08-07)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | drop the per-mutant list from a measured entry in mutation.py, which is today's code | a measured run satisfies the gate, and its absence still refuses |
| AC2 | write the measured per-mutant records but omit the `unit` key | a measured record is attributed to the unit that caused it |
| AC3 | write the measured records with the file and verdict but no line | the ledger records the shape the gate selects on |
| AC3 | write the measured records without the `unit` key, pinning the field where it is written | the ledger records the shape the gate selects on |
| AC4 | change transition.py to gate the contradiction check behind the mode being other than `off` | a ledger that contradicts itself refuses in every mode, `off` included |
| AC4 | change transition.py to refuse on any co-located registered and measured pair, whatever the two verdicts were | a ledger that contradicts itself refuses in every mode, `off` included |
| AC5 | change mutation.py to accept `--line` and drop it before writing the record | a registered mutant records a line, and a missing line is refused not defaulted |
| AC5 | change mutation.py to leave `--line` optional for a `survived` verdict | a registered mutant records a line, and a missing line is refused not defaulted |
| AC6 | change transition.py to compose the refusal from the target alone, dropping the line | the refusal quotes the line rather than a question mark |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-07 | sdlc-studio | Plan review round 1 REJECTed: AC1's test was vacuously green in both states until BG0541 wires the lane, so it is now a discriminating pair and BG0541 is a declared dependency; the mutant named only half the change, so AC2 is new for the attribution; AC3 gains its positive control; and AC4 makes `--line` mandatory for a non-equivalent verdict, without which the contradiction check silently never fires |
| 2026-08-07 | sdlc-studio | Plan review round 2 ruled four of five round-1 findings CLOSED and rejected on the new AC2: its Then was gate behaviour while its verifier named a `test_mutation.py` test that cannot drive `transition.py` - the very pattern that produced this wave's retractions - and an unattributed record was indistinguishable from an absent one. AC2 is now a CLI pair, AC3 carries the record-shape half where the record is written, and the refusal-quoting clause becomes AC6 in `test_transition.py` where the string is composed |
| 2026-08-07 | sdlc-studio | Plan review round 3 APPROVEd, ruling both round-2 findings CLOSED. Its minors are folded in: AC2's pair derives from one real run, AC6 names the survivor listing as the refusal under test, AC3 gains a row pinning the unit key where it is written, and the round-1 history row is marked against the renumbering |
| 2026-08-07 | sdlc-studio | Built. `ledger_entries` did not exist: `repair_mutation_gate` called it behind a `hasattr` that was False for its whole life, so the fallback was the only branch and any new caller reaching for it inside a `try` silently got nothing. Making `--line` mandatory reddened 16 existing tests, every one of them registering a mutant the shipped verb could not have produced - which is the criterion's own point, paid at its own expense |
| 2026-08-07 | sdlc-studio | Delivery review round 1 REJECTed on the finding that mattered most: `append_ledger` superseded every measured entry for a target, so two units declaring the same file - which is what a sprint touching one module looks like - meant the second unit's run silently erased the first unit's rows and shut its gate. Superseding is now per (target, unit), with a CLI test over two units and one file. The contradiction check keyed on the line alone, so two honest different mutants there read as the instrument lying - and because that branch ignores the mode by design, it turned the default reporting mode into a block no config could stand down. It now keys on the mutant too, with the differing-mutants control beside the agreeing one. `run --unit` had no test at all and its mutant survived; it has one now. `--line 0` is refused |
