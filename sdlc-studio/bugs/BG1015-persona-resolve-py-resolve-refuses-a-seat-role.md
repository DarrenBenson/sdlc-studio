# BG1015: persona_resolve.py resolve refuses a seat role the project declares (sre), though validate seats and critic.py brief accept it

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve_declared_roles.py, changelog.d/BG1015.md, .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py
> **Evidence:** persona_resolve.py `cmd_resolve` (~277) against `validate.check_seats` and critic.py's seat resolution; reproduced in a fixture.
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-09T09:22:30Z

## Summary

`persona_resolve.py resolve --seat <role>` checks the role against a fixed `SEATS` tuple (engineering, qa, product) before looking for the card, so a project that declares its own seat with `<!-- role: sre -->` is refused: 'unknown seat 'sre' (expected: engineering, qa, product)'. `validate seats` accepts the same card (errors=0) and `critic.py brief --seat` resolves project-declared seats. Reproduced at f3c928d4 in a fixture holding an sre seat card. A consuming project (homelab) declares an SRE seat, so its delegated worker cannot be framed through the shipped resolver. Found by the G10 breakdown and its panel review (D0355).

## Steps to Reproduce

Put a seat card with `<!-- role: sre -->` under sdlc-studio/personas/seats/; `persona_resolve.py resolve --seat sre --root <fixture>` -> 'unknown seat'.

## Proposed Fix

Accept any role a project seat card declares, as the consult path and critic do, keeping the fixed three only as the shipped defaults when the project declares none.

## Acceptance Criteria

- [ ] **AC1** `persona_resolve.py resolve --seat <role>` frames a worker from a project seat card declaring that role, for a role outside the shipped three
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve_declared_roles.py::DeclaredRoleTests::test_a_declared_sre_seat_resolves
- [ ] **AC2** A role no card declares and the skill does not ship is still refused, naming the declared roles
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve_declared_roles.py::DeclaredRoleTests::test_an_undeclared_role_is_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Filed |
