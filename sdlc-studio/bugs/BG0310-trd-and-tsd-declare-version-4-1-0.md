# BG0310: TRD and TSD declare version 4.1.0 against shipped 5.0.0 with the v5 architecture absent, and nothing gates spec version

> **Status:** Fixed
> **Verification depth:** functional (executable checks against the specs)
> **Severity:** Medium
> **Points:** 3
> **Affects:** sdlc-studio/trd.md
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

Both specs state 'the document version tracks the product version' yet declare 4.1.0 after 5.0.0 was cut: the TRD omits the v5 architecture entirely (goal ladder, plan-review pass D0061, run-archive D0043, delegated sign-off disclosure D0059), the TSD's Last Updated contradicts its own revision history and pins a test-noise baseline of 233 against the ratcheted 129, and no checker enforces any of it - `check_versions.py` never references prd/trd/tsd and the doc-freshness lane covers LATEST.md only.

## Steps to Reproduce

Evidence (trd.md header lines 4-6 and section 1 Coverage (lines 37-39); tsd.md header lines 4-6/17-18, lines 211-214, line 651): SKILL.md frontmatter version 5.0.0; package.json 5.0.0; CHANGELOG [5.0.0] 2026-07-26; sprint.py GOALS ladder and `_disclose_delegated_signoffs`, `run_state.py` `ARCHIVE_REL` - none in trd.md; tsd.md:4 'Version: 4.1.0', :5 'Last Updated: 2026-07-17' vs a 2026-07-24 revision row, :211-212 baseline 233 vs tools/skill-tests.sh `TEST_NOISE_BASELINE` 129; grep 'tsd|prd|trd' tools/`check_versions.py` returns nothing.

## Proposed Fix

Run a spec-truth refresh bringing TRD and TSD to 5.0.0 (documenting the goal ladder, plan review, run archive, delegated sign-off, and current baselines/headers), and extend `check_versions.py` or the doc-freshness lane to fail when a spec's declared version trails the shipped version.

## Acceptance Criteria

### AC1: every spec's version tracks the product version

- **Given** the PRD, TRD and TSD
- **When** the specs are read
- **Then** each declares the version SKILL.md declares, so the rule the documents state about themselves is one a checker reads
- **Verify:** shell python3 tools/check_versions.py
- **Verified:** yes (2026-07-29)

### AC2: a drifted spec is reported

- **Given** a fixture spec declaring an older version
- **When** the specs are read
- **Then** the guard reads it, so its discrimination is proven against a fixture rather than resting on the tree happening to be tidy
- **Verify:** pytest tools/tests/test_spec_versions_tracked.py::SpecVersionsTests::test_a_drifted_spec_is_reported
- **Verified:** yes (2026-07-29)

### AC3: a spec declaring no version is not a home

- **Given** a spec with no version line
- **When** the specs are read
- **Then** it is not held to the rule, so a project that never adopted the convention is not failed by it
- **Verify:** pytest tools/tests/test_spec_versions_tracked.py::SpecVersionsTests::test_a_spec_declaring_no_version_is_not_a_home
- **Verified:** yes (2026-07-29)

### AC4: both spellings of the version line are read

- **Given** the plain `**Version:**` the TRD uses and the blockquoted form the TSD uses
- **When** the specs are read
- **Then** both resolve, because a reader knowing one spelling would silently exempt the other
- **Verify:** pytest tools/tests/test_spec_versions_tracked.py::SpecVersionsTests::test_the_blockquoted_form_is_read_too
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
