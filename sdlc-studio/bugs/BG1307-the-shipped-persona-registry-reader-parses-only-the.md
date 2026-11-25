# BG1307: The shipped persona registry reader parses only the Primary, Secondary and Negative headings of `personas/index.md`, so a Served persona such as RFC0063's change approver is invisible to `status` and `hint`

> **Status:** Fixed
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py, changelog.d/BG1307.md
> **Evidence:** lib/sdlc_md.py:2768 docstring and the refusal at :2814 name only Primary/Secondary/Negative; the run nine product seat's grooming report
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T12:38:31Z

## Summary

Found by the product seat grooming CR0689 for run nine (2026-11-09). The registry reader in `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py` (around line 2768) parses `sdlc-studio/personas/index.md` into Primary, Secondary and Negative only, although the persona guide declares six cast roles including Served and Customer. When US1147 adds Graham Doyle under a Served heading (RFC0063 D3, D0437), `status` and `hint`, which read the registry through it, will not see him, and a consuming project with a Served or Customer persona has the same gap.

## Steps to Reproduce

1. In a scratch project, add a `## Served` heading to `sdlc-studio/personas/index.md` with one card listed under it.
2. Run the shipped status command against that project.
3. The Served persona is not reported; only the Primary, Secondary and Negative entries are.

## Proposed Fix

Read every cast role the persona guide declares (Primary, Secondary, Supplemental, Negative, Customer, Served) from the index, keep the existing roles' behaviour, and add a test that a Served entry is returned beside a control index holding only the three current roles.

## Acceptance Criteria

- [ ] **AC1** Given a `personas/index.md` with a `## Served` heading listing one card beside Primary, Secondary and Negative entries, when `sdlc_md.persona_registry` reads it, then the Served entry is returned with role `served` and its card path, beside the other three. Fails on: a Served persona invisible to every command that reads the registry.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::PersonaRegistryTests::test_a_served_entry_is_returned_beside_the_three_roles
  - **Verified:** yes (2026-11-24)
- [ ] **AC2** Given an index that also holds Supplemental and Customer headings, a `## Secondary (served, never at the Primary's expense)` heading and a `## Review seats` heading, when the reader parses it, then every cast role the persona guide declares is read under its own name, the parenthesis names no role, and no seat card is returned as a persona. Fails on: a role read from a heading's parenthesis, or a non-role heading's bullets registered.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::PersonaRegistryTests::test_every_declared_cast_role_is_read_and_a_parenthesis_names_none
  - **Verified:** yes (2026-11-24)
- [ ] **AC3** Given the control index holding only Primary, Secondary and Negative, when the reader parses it, then it returns exactly the entries and roles it returns today. Fails on: the wider grammar changing what an existing registry declares.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::PersonaRegistryTests::test_registry_parses_each_declared_role
  - **Verified:** yes (2026-11-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
