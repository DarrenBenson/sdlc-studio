# US0839: a risk trigger derived from Affects and unit type names which units still owe a consult, and most bugs skip without a reason

> **Status:** Won't Implement
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), RETIRE
> **Delivers:** RFC0058
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py
> **Epic:** EP0256
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** team lead adopting sdlc-studio on an inherited brownfield repo
**I want** a trigger that names which units still owe a consult, reporting and refusing nothing, with its rate measured on a real backlog first
**So that** I learn whether it over-fires before anything can stop my delivery on it

## Acceptance Criteria

D2 settled the trigger's inputs - `Affects` and the unit type - and its intent: most bugs, being
defects against settled intent, skip without a reason. It did not settle what happens where those
inputs are absent or inherited, which is the brownfield case. So this trigger ships ADVISORY, beside
`claim-drift` and `revert-check`, and carries a number measured over this repository's own backlog
before it is Done. It reads a unit's coverage only through US0840's stamped `> **Units:**` line and
treats any other shape as no coverage; D3, which would settle that shape, is open.

### AC1: the trigger reads both Affects and the unit type, and names the trigger that fired

- **Given** a fixture backlog of four units: a Bug whose `Affects` is `scripts/lib/sdlc_md.py` alone; a Bug whose `Affects` names `help/sprint.md`, text a user reads; a Story whose `Affects` is one test module; and a Story in an epic no stamped consult covers
- **When** `persona_resolve.py consult-owed --root <fixture>` runs through `main`
- **Then** every unit is reported owed or skipped with the trigger NAMED - `running-system`, `user-facing-text`, `stakeholder-origin` or `uncovered-epic` - the first Bug skips with no trigger fired, the second Bug is owed on `user-facing-text`, and the test-module Story is owed on `uncovered-epic` alone rather than on its files
- **Mutant:** derive the trigger from the unit type alone - every story is then owed and every bug skips, so a bug that changes what a user is told escapes, and `Affects`, which D2 names as half the derivation, contributes nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py::ConsultTriggerTests::test_the_trigger_reads_affects_and_the_unit_type

### AC2: a unit whose Affects cannot be used is undecidable, not a skip

- **Given** two further fixture units: one carrying no `Affects` line at all, and one whose `Affects` names a path present in no tree - an inherited line from a repository that has since moved its files
- **When** consult-owed runs
- **Then** both are reported `undecidable` with the reason naming which of the two shapes it hit, counted in a total of their own, and neither is counted among the owed or among the skipped
- **Mutant:** read an absent or unresolvable `Affects` as no trigger fired, so it skips - on a brownfield repo where `Affects` was never authored, the trigger then reports the whole backlog as owing nothing, and the adopter reads silence as coverage
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py::ConsultTriggerTests::test_an_unusable_affects_is_undecidable_rather_than_a_skip

### AC3: it reports and gates nothing, and no shipped script calls it

- **Given** a fixture backlog in which every unit is owed
- **When** consult-owed runs
- **Then** it exits 0 whatever it found, its output carries no refusal word, and a scan of the shipped `scripts/` tree finds the entry point called from its own module and its own tests alone - so the only refusal in EP0256 stays US0838's, on a refine that produced neither a consult nor a skip
- **Mutant:** exit non-zero when anything is owed - an instrument whose over-firing has not yet been measured becomes a gate nobody ruled, which is why `claim-drift` and `revert-check` both ship advisory while their yield is measured
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py::ConsultTriggerTests::test_the_trigger_reports_and_gates_nothing

### AC4: the rate is measured over this repository's own backlog before the story is Done

- **Given** this repository's real `sdlc-studio/` backlog, not a fixture
- **When** `persona_resolve.py consult-owed --census --root .` runs
- **Then** it prints owed, skipped and undecidable counts split by unit type; the delivery records those figures in this story's Revision History; and the story is not Done while more than half of Bugs are owed, D2 having ruled that most bugs skip
- **Mutant:** measure on the fixture alone - the fixture is built from D2's own words and so cannot over-fire, and the adopter learns the real rate across live delivery instead
- **Verify:** manual - the census figures from `persona_resolve.py consult-owed --census --root .`, recorded in this story's Revision History

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): RETIRE - [+constraint] risk trigger naming units that owe a consult: new obligation |
