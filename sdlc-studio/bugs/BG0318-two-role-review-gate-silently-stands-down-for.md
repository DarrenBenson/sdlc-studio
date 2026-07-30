# BG0318: Two-role review gate silently stands down for every schema-v3 (ULID) unit when review.two_role_after is set

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0
> **Audit-lens:** unknown
> **Audit-run:** wf_804ef18d

## Summary

`sdlc_md.id_number` returns None for a v3 ULID id, making `two_role_applies` False for every ULID unit, so on a schema-v3 project with `review.two_role_after` set both the evidence half and the sign-off half default to True unchecked - the forward-only cutoff fails open on exactly the newest units it exists to cover, with no warning, contradicting the non-negotiable that units past the cutoff hold at Review.

## Steps to Reproduce

Evidence (`_done_stages` lines 215-218 and `detect_conformance` lines 407-411): conformance.py:215-217 requires `rid_num` is not None for the gate to apply, then line 218 defaults both halves True; lib/`sdlc_md.py`:1252-1263 documents `id_number` returning None for ULIDs; verified by execution: `id_number(`'US-01JQK3F8') is None. Contrast `adopt_after` handling at lines 417-418, which fails safe on the same None.

## Proposed Fix

Fail closed: when `two_role_after` is set and `id_number` returns None, apply the two-role requirement to the unit (ULID ids are by construction newer than any numeric cutoff), or refuse the numeric-cutoff config on a v3 workspace with a clear error.

## Acceptance Criteria

### AC1: a ULID unit past the cutoff is held to both two-role halves

- **Given** `review.two_role_after` set and a Done unit carrying a v3 short-ULID id with no adversarial evidence and no sign-off
- **When** the Done stages are computed
- **Then** `critiqued` is False and both unmet halves are named
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::TwoRoleCutoffOnUlidIdsTests::test_a_ulid_unit_past_the_cutoff_is_held_to_both_two_role_halves

### AC2: the verdict does not depend on which id era the project mints

- **Given** the same evidence and the same cutoff, once for a ULID id and once for a v2 sequential id past the cutoff
- **When** both are judged
- **Then** the unmet-half lists are identical
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::TwoRoleCutoffOnUlidIdsTests::test_the_ulid_verdict_matches_the_v2_verdict_for_the_same_evidence

### AC3: failing closed does not become always-on

- **Given** a project with no `review.two_role_after` configured
- **When** a ULID unit is judged
- **Then** no two-role half is required of it, so an unconfigured project is untouched
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::TwoRoleCutoffOnUlidIdsTests::test_no_cutoff_configured_still_leaves_a_ulid_unit_alone

### AC4: the report an operator reads shows the gate applying

- **Given** a workspace with the cutoff set, a Definition of Done that downgrades the critic half only, and a Done ULID story
- **When** `detect_conformance` runs
- **Then** `critiqued` is reported missing for that unit, so the second copy of the comparison (the required-stage list) is fixed too
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::TwoRoleCutoffOnUlidIdsTests::test_end_to_end_a_done_ulid_story_is_not_reported_conformant

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
| 2026-07-28 | delivery lane (RUN-01KYJZGZ) | Acceptance criteria authored; fix + regression tests landed |
