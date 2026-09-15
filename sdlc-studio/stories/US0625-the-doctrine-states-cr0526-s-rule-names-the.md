# US0625: the doctrine states CR0526's rule, names the one store a stop-ship ruling lives in, and who rules it

> **Status:** Ready
> **Delivers:** CR0526
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-doctrine.md, tools/tests/test_doctrine_stop_ship.py
> **Epic:** EP0206
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** reviewer of record deciding whether a finding stops a release
**I want** the doctrine to state CR0526's rule, the one table a stop-ship ruling is recorded in, and who rules it (D0194)
**So that** a release decision rests on a ruling somebody made against a named finding, rather than on a severity label read later

## Acceptance Criteria

### AC1: the doctrine states CR0526's rule, both outcomes

- **Given** reference-doctrine.md
- **When** the stop-ship rule is read
- **Then** it states that a finding NOT ruled stop-ship becomes its own filed artefact and its unit closes pointing at it, that a finding ruled stop-ship holds the close, and that severity alone is not the ruling
- **Mutant:** delete the sentence naming what happens to a non-stop-ship finding - the rule survives only as practice, the state LL0027 names
- **Verify:** pytest tools/tests/test_doctrine_stop_ship.py::StopShipDoctrineTests::test_the_rule_names_both_outcomes

### AC2: the doctrine names the one store and who rules (D0194)

- **Given** the same passage
- **When** it is read
- **Then** it names the retro's Known issues carried table as the ONLY place a stop-ship ruling is recorded, the operator or a recorded delegate as who rules, and says a reviewer's proposal in a finding is not a ruling
- **Mutant:** name the critic ledger as a second store - the ruling a reader follows is then one the close never reads
- **Verify:** pytest tools/tests/test_doctrine_stop_ship.py::StopShipDoctrineTests::test_the_one_store_and_the_ruler_are_named

### AC3: the table the doctrine names is the one the close reads

- **Given** the section name and ruling vocabulary the doctrine quotes
- **When** the test reads them
- **Then** they are compared against `retro.KNOWN_ISSUES_SECTION` and `retro.KNOWN_ISSUE_RULINGS`, read from the code rather than restated (LL0042)
- **Mutant:** rename the section constant in retro.py - the doctrine then names a table the close does not read, and a restated test would stay green
- **Verify:** pytest tools/tests/test_doctrine_stop_ship.py::StopShipDoctrineTests::test_the_named_table_is_the_one_the_close_reads

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-15 | sdlc-studio | Retitled: was 'the doctrine states the rule and the stop-ship judgement is recorded per finding at review time' |
| 2026-09-15 | sprint planning 2026-09-15 | Re-groomed at the sprint goal review (round 1: all three seats refused a goal carrying CR0526) against D0193 (an unfinished unit feeds the close's stop-ship step, not a third gate) and D0194 (one stop-ship store, the retro's carried table). Shrunk to the doctrine: the per-finding critic-ledger store it specified would have been a second store nothing reads. 3 -> 2 points. |
