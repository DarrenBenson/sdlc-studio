# US1340: A seat corrects a fact in the document it reviews against and proposes any change to what it requires

> **Status:** Done
> **Depends on:** US1339
> **Risk-class:** standard
> **Delivers:** CR0755
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-workflow-personas.md, tools/tests/test_lean_seat_change_authority.py, changelog.d/US1340.md
> **Epic:** EP0384
> **Points:** 1
> **Persona:** Abena Osei

## User Story

**As a** head of engineering who answers for every release at the change board (Abena)
**I want** the skill to say what a seat may change in the document it reviews against, and what
it must put to the person
**So that** every change to a requirement names an accountable person, while a seat still keeps
the document's facts current without waiting on anyone

The seats section says what a seat's delegated authority lets it change in the document it
reviews against. It may correct a fact itself (a feature's status, a criterion verified work
has met, a count, a date, a link): the same changes the review already applies without
confirmation. A change to what the document requires (a requirement added, removed or
reworded, a priority, the scope) it proposes as a change request carrying the wording, and the
person decides: a seat never writes the requirements it signs against. A seat unsure which kind
a change is treats it as a proposal and asks the person.

## Acceptance Criteria

### AC1: A seat may correct a fact in its document

- **Given** the seats section of reference-workflow-personas.md
- **When** it is read for what a seat may change in the document it reviews against
- **Then** it says a seat's delegated authority lets it correct a fact in that document (a
  feature's status, a criterion verified work has met, a count, a date or a link), and it links
  to the review's auto-apply step (step 3b of reference-review.md) as the place those
  corrections are made. Fails on: no passage in reference-prd.md, reference-pvd.md,
  reference-review.md or reference-workflow-personas.md says what a seat may change in the
  document it reviews against ("change of fact" or "correct a fact": 0 hits; a seat near "edit"
  or "change" near PRD or PVD: 0 hits), and the seats section (lines 117-132) has no link to
  reference-review.md.
- **Verify:** pytest tools/tests/test_lean_seat_change_authority.py::SeatChangeAuthorityTests::test_a_seat_may_correct_a_fact_in_its_document
- **Verified:** yes (2026-11-26)

### AC2: A change to a requirement is proposed and the person decides

- **Given** the same section
- **When** it is read for a change to what the document requires
- **Then** it says such a change (a requirement added, removed or reworded, a priority, or the
  scope) is one the seat proposes as a change request carrying the wording, that the person
  decides it, and that a seat never writes the requirements it signs against. Fails on: no
  passage in those four pages says a seat proposes a change to the PRD or the PVD ("propos"
  followed by "change": 0 hits).
- **Verify:** pytest tools/tests/test_lean_seat_change_authority.py::SeatChangeAuthorityTests::test_a_change_to_a_requirement_is_proposed_and_the_person_decides
- **Verified:** yes (2026-11-26)

### AC3: A seat unsure of the kind of change proposes it and asks

- **Given** a seat that cannot tell whether a change is a correction of fact or a change to a
  requirement
- **When** the seats section is read for what it does
- **Then** one sentence says it treats the change as a proposal and asks the person: the test
  requires "unsure" or "cannot tell" together with "propos" in that sentence, so US1339's "asks
  the person when unsure" alone does not satisfy it. Fails on: at HEAD the four pages carry no
  "unsure" at all; after US1339, only a sentence that does not tie being unsure to proposing.
- **Verify:** pytest tools/tests/test_lean_seat_change_authority.py::SeatChangeAuthorityTests::test_a_seat_unsure_of_the_kind_proposes_and_asks
- **Verified:** yes (2026-11-26)

## Notes

- Ruling: D0636 (the operator, 2026-11-26) chose this reading: a seat corrects facts itself,
  proposes any change to a requirement, priority or scope as a change request the person
  decides, and asks when unsure which kind a change is.
- Suggested wording for the builder, added to the seats section US1339 rewrites; the tests pin
  meaning, not exact prose: "A seat's delegated authority lets it correct a fact in the document
  it reviews against: a feature's status, a criterion that verified work has met, a count, a
  date or a link. These are the changes the review applies without confirmation (step 3b of
  `reference-review.md`). A change to what the document requires, such as a requirement added,
  removed or reworded, a priority or the scope, the seat proposes as a change request carrying
  the wording, and the person decides it: a seat never writes the requirements it signs
  against. A seat unsure which kind a change is treats it as a proposal and asks the person."
- The link to step 3b uses the heading's implicit slug ("### 3b. Auto-Apply Mechanical Fixes");
  `tools/check_links.py` indexes implicit slugs, so it refuses a link that does not resolve.
  Step 3b itself already matches this rule and is not changed.
- Depends on US1339, which renames the seats section and edits the same lines; the planner
  treats a shared `.md` as advisory and will not sequence the two by itself.
- Out of scope under D0636: `prd review` (reference-prd.md), a command the person runs, keeps
  adding newly discovered features as a direct edit, so this story does not touch it. The shipped
  product seat card already says the seat never authors the PRD and is not changed. A file
  outside Affects that needs a change is a finding to report, not an edit.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-26 | product seat | Groomed for run twenty-eight under D0636 |
