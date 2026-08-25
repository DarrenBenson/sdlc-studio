# US0686: The entry refusal names WHEN the independent approval will be demanded, so the move is not a silent relaxation

> **Status:** Blocked
> **Delivers:** CR0555
> **Created:** 2026-08-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Epic:** EP0218
> **Blocked by:** a pre-code goal review, and then by a measurement that invalidated the request's premise. `transition.py:961` gates the two-role delivery review as story-and-Done only, so a bug pays no second review cycle for this batch to merge - and a further dry-run across all 23 open bugs found that NONE owes an independent review at all, because the entry gate never fires for a bug. CR0555 is narrowed to STORIES, where the two-cycle saving is real. These units are kept for their review record: eleven further findings, including that all twenty of their criteria were library tests rather than lane tests (LL0040). Re-groom against the narrowed request before building. Disposition: the entry refusal message - survives; merge candidate with US0685, which edits the same string.
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The entry refusal names WHEN the independent approval will be demanded, so the move is not a silent relaxation
**So that** CR0555 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a unit refused at entry for having no test plan, when the refusal is printed, then it NAMES that an independent approval will be demanded at the terminal transition - a relaxation nobody is told about reads as a gate that was switched off
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::EntryRefusalMessageTests::test_the_entry_refusal_names_the_later_approval_demand
- [ ] **AC2** Given that refusal, when it is printed, then it names the command that records the approval, and running that command clears the terminal gate - asserted by RUNNING it, because a message naming a command that does not work is the same defect one step later
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::EntryRefusalMessageTests::test_the_named_command_clears_the_terminal_gate
- [ ] **AC3** Given a unit that PASSES the entry gate, when it passes, then nothing is printed about the later demand - the paired control, because a message on every transition is one nobody reads
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::EntryRefusalMessageTests::test_a_passing_entry_says_nothing

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-25 | sdlc-studio | Created via `new` (deterministic) |
