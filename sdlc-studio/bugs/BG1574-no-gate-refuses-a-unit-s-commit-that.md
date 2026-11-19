# BG1574: No gate refuses a unit's commit that ships no changelog fragment, so run sixteen landed twelve of fourteen units without one

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .githooks/pre-commit, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/refine.py, tools/tests/test_changelog_fragment_required.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py, changelog.d/BG1574.md
> **Evidence:** Run sixteen (RUN-01M7NTY5), 2026-11-18: commits 79519227 (has one), cb445223, b10e40ae, 85b79786 (none).
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T01:05:23Z

## Summary

AGENTS.md says every behaviour or doc change carries its changelog.d/<UNIT-ID>.md fragment (LL0004), but the pre-commit's changelog-shape lane checks only the shape of fragments that are staged. Grooming left the fragment out of most bugs' Affects, builders stage exactly the Affects, and lane land, critic brief and lane accept all passed units with none. Run sixteen landed BG1507, BG1519 to BG1524, US1290 to US1292 and BG1523 with no fragment; two reviewers flagged it as non-blocking, and the fragments were written afterwards in a paperwork commit.

## Steps to Reproduce

Groom a bug whose Affects omit changelog.d/<ID>.md; build and land it through sprint lane land; observe the commit pass and the unit reach Fixed.

## Proposed Fix

Have the commit-msg or pre-commit refuse a commit whose subject names a unit with a behaviour change but stages no changelog.d/<ID>.md for it (a docs-only or test-only unit can declare an exemption), and have refine and the groom add the fragment to Affects by default.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: AGENTS.md says every behaviour or doc change carries its changelog.d/<UNIT-ID>.md fragment (LL0004), but the pre-commit's changelog-shape lane checks only the...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Groom a bug whose Affects omit changelog.d/<ID>.md; build and land it through sprint lane land; observe the commit pass and the unit reach Fixed.
- [ ] **AC3** The proposed fix lands, pinned by a test: Have the commit-msg or pre-commit refuse a commit whose subject names a unit with a behaviour change but stages no changelog.d/<ID>.md for it (a docs-only or...

## Impact

The release cut's CHANGELOG misses the unit, or the fragment is written later by someone who did not build it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
