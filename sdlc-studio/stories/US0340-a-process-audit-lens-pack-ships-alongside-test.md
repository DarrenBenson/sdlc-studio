# US0340: A process audit lens pack ships alongside test, with lenses drawn from failures this project actually produced

> **Status:** Draft
> **Depends on:** BG0265, BG0256
> **Delivers:** CR0403
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/audit-profiles/process.md,.claude/skills/sdlc-studio/scripts/audit.py,.claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py
> **Epic:** EP0115
> **Points:** 5

## User Story

**As an** operator auditing a delivery whose tests and prose already have a lens pack
aimed at them
**I want** a `process` profile that attacks the way the work was produced rather than
what it claims
**So that** the failure this skill exists to prevent - work done before the contract it
depends on was established - is hunted by the same machinery as every other failure
class, instead of resting on the author's discipline

## Context

The pack is a sibling of `test`, not a new mechanism: `audit.py` already resolves a
profile, parses a declarative lens table and refuses a name no pack declares. What is
missing is the pack itself and its wiring - resolution, the shared refute panel, and the
two catalogues a reader looks in.

The roster of lenses is left to grooming rather than pinned here. What the criteria hold
is that whatever roster ships is declarative, panel-wired, discoverable, and refused when
it is empty. Whether each lens is drawn from a failure this project actually produced is
held by US0342, which binds every lens to a recorded incident - a citation that resolves
is the mechanical proxy for "not invented", and the closest one available.

## Acceptance Criteria

### AC1: the pack resolves as a named profile and is listed everywhere profiles are listed

- **Given** the shipped skill tree with `templates/audit-profiles/process.md` in it
- **When** `audit.resolve_profile("process")` runs, and the reference and help catalogues
  are read
- **Then** the profile resolves to `templates/audit-profiles/process.md` with a non-empty
  lens set, `profile_names()` includes it, and both catalogues list it - so no leg of the
  surface can ship without the others
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py::ProcessProfileTests::test_the_process_profile_resolves_and_is_catalogued_wherever_profiles_are_listed

### AC2: every lens is declarative in the same shape as its sibling packs

- **Given** the parsed pack
- **When** each lens row is read
- **Then** every lens carries an adversarial question that is a question and a non-empty
  statement of what it hunts, and the pack's columns match the shipped `test` pack's, so a
  finder handed this pack gets the same fields as any other
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py::ProcessProfileLensTests::test_every_process_lens_declares_a_question_and_what_it_hunts

### AC3: the pack is panel-wired and hands the finder the file-or-decline discipline

- **Given** the pack as shipped
- **When** it is resolved
- **Then** it declares the shared refute threshold of 2 of 3 and states that it does not
  opt out, and it carries the file-or-decline discipline verbatim, so a surviving candidate
  is either filed or declined with a reason rather than lost in the run report
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py::ProcessProfileTests::test_the_process_pack_is_panel_wired_and_states_file_or_decline

### AC4: a pack whose lens table is gone is refused, not reported clean

- **Given** a fixture copy of the pack with every table row stripped out
- **When** the profile is resolved, and `audit profile --name process` runs against it
- **Then** resolution raises `UnknownProfile` naming the pack path, and the command exits
  non-zero saying the pack declares no lens - an empty process audit must never read as a
  clean one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py::ProcessProfileTests::test_a_lensless_process_pack_is_refused_rather_than_run

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
