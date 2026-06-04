<!--
Template: Bug Report (Streamlined)
File: sdlc-studio/bugs/BG{NNNN}-{slug}.md
Status values: See reference-outputs.md
Related: help/bug.md, reference-bug.md
-->
# BG{{bug_id}}: {{title}}

> **Status:** {{status}}
> **Severity:** {{severity}}
> **Priority:** {{priority}}
> **Reporter:** {{reporter}}
> **Assignee:** {{assignee}}
> **Created:** {{created_date}}
> **Verification depth:** {{verification_depth}}

## Summary

{{summary}}

## Affected Area

- **Epic:** [EP{{epic_id}}: {{epic_title}}](../epics/EP{{epic_id}}-{{epic_slug}}.md)
- **Story:** [US{{story_id}}: {{story_title}}](../stories/US{{story_id}}-{{story_slug}}.md)
- **Component:** {{component}}

## Environment

- **Version:** {{version}}
- **Platform:** {{platform}}

---

## Reproduction Steps

1. {{step_1}}
2. {{step_2}}
3. {{step_3}}

## Expected Behaviour

{{expected_behaviour}}

## Actual Behaviour

{{actual_behaviour}}

---

## Root Cause Analysis

> *Filled when investigating*

{{root_cause}}

## Fix Description

> *Filled when fixing*

{{fix_description}}

### Files Modified

| File | Change |
|------|--------|
| {{file_path}} | {{change_description}} |

### Tests Added

| Test | Description | File |
|------|-------------|------|
| TC{{test_id}} | {{test_description}} | {{test_file}} |

---

## Verification

- [ ] Fix verified in development
- [ ] Regression tests pass
- [ ] No side effects observed

**Verified by:** {{verifier}}
**Verification date:** {{verification_date}}
**Verification depth:** {{verification_depth}}

> Verification depth tiers: `smoke` (one-shot ping) | `functional` (single round-trip) | `conversational` (multi-turn / multi-step) | `soak` (live traffic over a window) | `live` (operator-confirmed in production with no rollback). See `reference-test-best-practices.md#verification-depth-tiers`. A bug cannot be marked **Fixed** until depth is at least `functional`. A production-affecting bug cannot be **Closed** until depth is at least `soak` (default 7 days).

---

## Revision History

| Date | Author | Change |
|------|--------|--------|
| {{created_date}} | {{reporter}} | Bug reported |
