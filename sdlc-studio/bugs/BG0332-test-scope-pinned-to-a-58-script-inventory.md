# BG0332: Test scope pinned to a 58-script inventory when the tier ships 70

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
> **Severity:** Low
> **Points:** 2
> **Affects:** sdlc-studio/tsd.md
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0
> **Audit-lens:** unknown
> **Audit-run:** wf_804ef18d

## Summary

Both specs define the script-tier surface as 58 scripts while scripts/ contains 70 top-level helpers; because the TSD concedes no sweep enforces per-script coverage, this pinned count is the only inventory bounding the unit-test scope and it is ~17% short, in documents whose stated rule is not to pin drifting numbers.

## Steps to Reproduce

Evidence (In Scope line 67 and Test Organisation line 616; same figure in prd.md line 94): tsd.md:67 and :616-617 plus prd.md:94-95 pin 58; ls .claude/skills/sdlc-studio/scripts/*.py | wc -l returns 70; tsd.md:220-222 concedes the absence of an enforcing sweep.

## Proposed Fix

Replace the pinned 58 with the current count or unpinned wording ('the shipped helpers under scripts/') in both tsd.md and prd.md.

## Acceptance Criteria

### AC1: the specs state the script tier as a SET, not a count

- **Given** the TSD and TRD live prose (the revision history is a record, not a live claim)
- **When** the guard runs
- **Then** no pinned component count disagrees with the census, so the only inventory bounding the unit-test scope cannot silently go a fifth short
- **Verify:** pytest tools/tests/test_spec_counts_are_not_pinned.py::SpecCountsTests::test_no_spec_pins_a_component_count_it_does_not_match
- **Verified:** yes (2026-07-29)

### AC2: the guard compares against the census, not a second written number

- **Given** the census of scripts and lib modules
- **When** the guard runs
- **Then** it is read from the tree and asserted non-trivial, because a guard carrying its own copy of the count is the defect it exists to catch
- **Verify:** pytest tools/tests/test_spec_counts_are_not_pinned.py::SpecCountsTests::test_the_census_is_readable
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
