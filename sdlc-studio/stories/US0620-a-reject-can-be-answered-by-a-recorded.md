# US0620: a REJECT can be answered by a recorded REPAIR naming the findings it closes and the evidence closing each

> **Status:** Review
> **Delivers:** CR0506
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0205
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** an author whose unit was rejected and then repaired
**I want** the repair recorded against the verdict, naming each finding it closes and how
**So that** what the reviewer found and what was done about it are both visible in one place

## Notes

Delivers criterion 1 of CR0506, and it is the foundation the rest of EP0205 stands on: US0621's
three-state predicate has nothing to read until this record exists.

The record is **append-only and does not overwrite the REJECT**. What the reviewer found stays
true; what was done about it becomes visible beside it. A repair that replaced the verdict would
destroy the only evidence that the review happened at all - which is the failure this epic exists
to end, not to repeat from the other direction.

Evidence per finding is one of three shapes, taken from the CR: the reviewer's own mutant
re-applied and killed, a test that now reddens, or the artefact id the residue was filed as.
LL0045 is the discipline being mechanised - rule each finding CLOSED, OVER-CLAIMED or MOVED,
rather than declaring the set repaired.

It belongs in `critic.py` beside the verdict, not in a new ledger. The whole value is that a
reader of the verdict sees the disposition without knowing to look elsewhere, and `BG0499` in
this same batch is what happens when two ledgers hold halves of one answer.

## Acceptance Criteria

### AC1: a repair records per-finding closure with its evidence

- **Given** a unit carrying a recorded REJECT with several findings
- **When** a repair is recorded
- **Then** it names each finding it closes and the evidence closing it - a re-applied mutant, a
  test that now reddens, or a filed artefact id - and a repair naming a finding the verdict never
  raised is refused, because a disposition that matches nothing is not a disposition
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::RepairRecordTests::test_a_repair_names_each_finding_it_closes_with_its_evidence
- **Verified:** yes (2026-08-03)

### AC2: the REJECT survives the repair, verbatim

- **Given** a recorded REJECT
- **When** a repair is recorded against it
- **Then** the verdict, its reviewer, its brief provenance and its findings are byte-identical
  afterwards, and the repair reads as a separate appended record - what the reviewer found stays
  true, and no repair route can quietly become an edit route
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::RepairRecordTests::test_the_reject_survives_the_repair_byte_identically
- **Verified:** yes (2026-08-03)

### AC3: the record carries its own author and is refused without one

- **Given** a repair being recorded
- **When** no author is supplied
- **Then** it is refused - a repair is a claim about work somebody did, and an unattributed claim
  cannot be questioned, which is the same rule the verdict already holds
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::RepairRecordTests::test_an_unattributed_repair_is_refused
- **Verified:** yes (2026-08-03)

### AC4: the repair is visible from the verdict, through the shipped command

- **Given** a unit with a REJECT and a repair
- **When** `critic.py show --unit <id>` runs
- **Then** the output carries both, so a reader of the verdict sees the disposition without
  knowing a second command exists - asserted through the CLI, because a library-only check cannot
  see a record the shipped reader never prints
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::RepairRecordTests::test_show_prints_the_repair_beside_the_verdict
- **Verified:** yes (2026-08-03)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-03 | Claude Opus 5 | Groomed against CR0506 criterion 1, with AC4 driving the shipped CLI rather than the library after LL0040 |
