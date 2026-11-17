# BG1526: The PRD flags table gives wrong defaults for lessons.loop and schema_version

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** sdlc-studio/prd.md, tools/tests/test_lean_prd_refresh.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, prd lens, survived 3 of 3 refute votes; observed at sdlc-studio/prd.md Section 9 Feature Flags table, line 668 (`lessons.loop`) and line 675 (`schema_version`)
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:22:37Z

## Summary

The Feature Flags table in the PRD is introduced as showing the defaults in `templates/config-defaults.yaml`, and two of its rows do not match that file. The `lessons.loop` row gives the default as loop, but the shipped default and the documented vocabulary are enforce and judgement; loop is not a documented value and behaves as blocking only because `gate.py` treats anything other than judgement as blocking. The `schema_version` row gives 3, but the shipped fallback is 2, and only the init template stamps 3 on a new project. A project that pulls the skill without the key is therefore on version 2 behaviour, with no distributed ids and no inbox lane, while the PRD tells the reader the default is distributed identity.

## Steps to Reproduce

1. Read sdlc-studio/prd.md line 668: the `lessons.loop` row gives the default loop.
2. Read sdlc-studio/prd.md line 675: the `schema_version` row gives the default 3.
3. Read .claude/skills/sdlc-studio/templates/config-defaults.yaml lines 12 and 360: `schema_version: 2` and `loop: enforce`.
4. Run config.py show with --key lessons.loop and then with --key `schema_version` in an empty root: it prints enforce and 2.
5. Read reference-config.md at about lines 271 and 643: both agree with the defaults file, not with the PRD.

## Proposed Fix

Change the `lessons.loop` row's default to enforce. Change the `schema_version` row to say the fallback default is 2 and that `init` stamps 3 on a new project, so both facts are stated. Add a check to the PRD refresh test that reads these two keys from the defaults file and fails when the PRD row gives a different value.

## Acceptance Criteria

- [ ] **AC1** Given the Feature Flags table of `sdlc-studio/prd.md` and `templates/config-defaults.yaml`, when the `lessons.loop` and `schema_version` rows are compared with the defaults file, then `lessons.loop` gives enforce, and `schema_version` gives the fallback default 2 and says `init` stamps 3 on a new project. Fails on: either row giving a default the defaults file does not hold.
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::PrdFlagDefaultsTests::test_the_lessons_loop_and_schema_version_rows_match_the_defaults_file

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
