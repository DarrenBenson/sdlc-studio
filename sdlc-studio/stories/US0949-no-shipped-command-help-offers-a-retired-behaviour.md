# US0949: No shipped command help offers a retired behaviour

> **Status:** Draft
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_retired_help.py, changelog.d/US0949.md, .claude/skills/sdlc-studio/scripts/tests/test_create_validate_roundtrip.py, .claude/skills/sdlc-studio/scripts/tests/test_planning_tier.py, .claude/skills/sdlc-studio/help/sprint.md
> **Epic:** EP0265
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer who learns a command from its --help
**I want** `sprint close`, `sprint call` and `artifact new` to describe only what they still do
**So that** an agent reading the help never reaches for a flag that exits 2 or writes a field nothing reads

## Acceptance Criteria

- **AC1:** Given `sprint.py close --help` and `sprint.py call --help`, when each is printed, then neither describes `--apply-signoff` as fanning or recording a sign-off, and `sprint.py call` no longer forwards `--apply-signoff` to the close (the close still exits 2 on it, naming `sprint.py sign`). Fails on: HEAD, where the close's help (sprint.py:11322-11328) says the flag fans reviewer-of-record sign-offs and `call` appends it to the close argv (sprint.py:11100, back-to-basics defect 14); and on a fix that only rewords the close help while `call` still forwards the flag
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_retired_help.py::RetiredHelpTests::test_close_and_call_do_not_offer_apply_signoff
- **AC2:** Given `artifact.py new --type story --target soak`, when it runs, then it exits 2 with a message that the verification-target tier is retired, writes nothing, and `artifact.py new --help` no longer lists `--target`; a story created without the flag carries no `Verification target` line. Fails on: removing the template line (US0924) while the flag still writes `Verification target` on every supplied AC (artifact.py:372)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_retired_help.py::RetiredHelpTests::test_verification_target_tier_is_retired

## Notes

Measured at 013a46d0: `close --apply-signoff` exits 2 (sprint.py:8890-8896) but its help and `call`'s forwarding still describe the retired fan-out. Ratchet (LC-008): the `--target` refusal follows the established retired-verb shape (exit 2 naming what replaced it) and retires a field nothing reads; no new lane. File-disjoint from US0924 (docs only).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 5 from the seat planning (U6) |
