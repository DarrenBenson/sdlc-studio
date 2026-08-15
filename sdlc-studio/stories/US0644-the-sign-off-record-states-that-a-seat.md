# US0644: The sign-off record states that a seat signed and names it, so no reader mistakes it for a human

> **Status:** Done
> **Delivers:** CR0532
> **Created:** 2026-08-05
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py,.claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_critic.py
> **Epic:** EP0209
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The sign-off record states that a seat signed and names it, so no reader mistakes it for a human
**So that** CR0532 is delivered by work that can be planned and checked

## Acceptance Criteria

> **Grooming note.** A panel sign-off today is distinguishable only by string-matching the
> `panel(...)` marker inside the free-text `chain` column. That is a fact a reader can find and a
> filter cannot rely on.

### AC1: the record carries the capacity as a parsed field

- **Given** a panel sign-off
- **When** the row is read back through the shipped reader
- **Then** the returned record carries a capacity of `seat` and names the signing seat, without any caller parsing prose
- **Mutant:** keep the marker in `chain` alone - the field is absent and the read-back assertion reddens
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::SignoffCapacityTests::test_a_panel_signoff_records_capacity_seat
- **Verified:** yes (2026-08-05)

### AC2: a human sign-off is distinguishable in the same field

- **Given** an ordinary operator sign-off
- **When** it is read back
- **Then** the capacity is `human`, so a consuming project filters on one field rather than on the absence of a marker
- **Mutant:** write the capacity only for panels - "not a seat" and "old record" become the same answer
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::SignoffCapacityTests::test_a_human_signoff_records_capacity_human
- **Verified:** yes (2026-08-05)

### AC3: a historical row with no capacity never reads as a seat

- **Given** a row written before this change
- **When** it is read back
- **Then** the capacity reads as unknown or human, never as `seat`, because the direction this must not fail in is a machine's signature being taken for a person's
- **Mutant:** default an absent capacity to `seat` - every historical sign-off in the corpus reads as an AI's
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::SignoffCapacityTests::test_an_absent_capacity_never_reads_as_seat
- **Verified:** yes (2026-08-05)

### AC4: the added column does not break the existing reader

- **Given** the sign-off record carrying the new column
- **When** every existing sign-off consumer reads it
- **Then** each still resolves the unit, principal, author and chain it read before
- **Mutant:** append the column without widening the declared column tuple - the parser mis-aligns every field after it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::SignoffCapacityTests::test_the_existing_columns_still_parse_and_the_gate_still_reads_them
- **Verified:** yes (2026-08-05)

### AC5: the parsed field reaches the RECORD, not just the return value

- **Given** a sign-off recorded through the shipped verb
- **When** the written record is read back
- **Then** it carries the unit, the principal and the author - a figure held only in a return value is one the next reader cannot see
- **Mutant:** keep the parsed field in memory and never write it - the in-process assertion passes and the file the next command opens has nothing in it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_critic.py::US0644TheCapacityReachesTheWrittenRecord
- **Verified:** yes (2026-08-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Created via `new` (deterministic) |
