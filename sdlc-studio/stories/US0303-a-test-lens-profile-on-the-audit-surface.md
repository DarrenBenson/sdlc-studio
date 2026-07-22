# US0303: A test lens profile on the audit surface, attacking claims code and tests assert about themselves

> **Status:** Review
> **Delivers:** CR0382
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/audit.py,.claude/skills/sdlc-studio/templates/audit-profiles/test.md,.claude/skills/sdlc-studio/reference-audit.md,.claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py
> **Epic:** EP0101
> **Points:** 5

## User Story

**As a** maintainer whose evidence for a change is the test suite that covers it
**I want** an audit profile whose lenses attack what tests, docstrings and comments
claim about themselves
**So that** prose that misdescribes the code it sits beside can be hunted deliberately,
which is the one failure class the mutation gate is structurally blind to

## Context

CR0382 adopts a fifth lens profile, `test`, on the existing pluggable audit surface
(`project` / `skill` / `repo` / `code`). This story is the surface: the pack exists,
resolves, is refute-gated like every other pack, refuses to run empty, and carries the
file-or-decline discipline that the finder agent is handed. The lens content itself is
US0304.

A mutant cannot detect a docstring that lies, so the value of this profile is entirely
in the lenses being run at all. That makes the failure mode to design against a `test`
run that reports a clean audit having examined nothing - the same false-green class the
existing `resolve_profile` refusal already guards for the other packs. AC3 attacks that
directly rather than the happy path.

## Acceptance Criteria

### AC1: `test` is a resolvable profile alongside the four that ship

- **Given** the shipped lens packs `project`, `skill`, `repo` and `code`
- **When** `audit.py profile --list` runs, and `audit.py profile --name test` resolves
- **Then** `test` appears in the listed profiles and resolves to
  `templates/audit-profiles/test.md`, reporting a non-zero lens count
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py::TestProfileTests::test_test_profile_is_listed_and_resolves_to_its_pack
- **Verified:** yes (2026-07-22)

### AC2: the pack faces the same refute panel as every other profile

- **Given** the shared refute panel - 3 skeptics per candidate, survive on >= 2 of 3
- **When** the `test` pack is resolved
- **Then** it declares that threshold and states it does not opt out, so a candidate
  raised by a `test` lens is held to the same burden as one from `code` or `repo`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py::TestProfileTests::test_test_pack_declares_the_shared_refute_threshold
- **Verified:** yes (2026-07-22)

### AC3: a lens-less pack is refused, never run as a clean audit

- **Given** a `test` pack whose lens table has been emptied or broken by a later edit
- **When** the profile is resolved
- **Then** resolution raises `UnknownProfile` naming the pack as the source, and the CLI
  exits non-zero, rather than reporting an audit that examined nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py::TestProfileTests::test_a_lensless_test_pack_is_refused_rather_than_run
- **Verified:** yes (2026-07-22)

### AC4: file-or-decline is stated in the pack the finder is handed

- **Given** the file-or-decline discipline in `reference-audit.md` - a surviving candidate
  is filed through `file_finding.py` or declined with a stated reason
- **When** the pack is read
- **Then** it states that discipline in the text the finder receives, so silence on a
  candidate is not a permitted outcome of a `test` run
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py::TestProfileTests::test_the_pack_states_file_or_decline
- **Verified:** yes (2026-07-22)

## Resolved Questions

- **Default scope: source and tests together** (D0053). The failure modes this lens
  attacks are claims written in prose about code, and they sit in source at least as
  often as in test files, so scoping the pack to test files alone would exclude the
  larger half of its own evidence. The pack states the default and says how to narrow it
  for a test-only change.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Built: `test` pack on the profile surface; scope ruling recorded (D0053); ACs verified |
