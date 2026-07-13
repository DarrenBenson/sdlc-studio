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
> **Affects:** {{source files this fix touches, comma-separated}}

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

## Steps to Reproduce

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

## Proposed Fix

> *Proposed at filing; refined when fixing*

{{fix_description}}

### Files Modified

| File | Change |
| --- | --- |
| {{file_path}} | {{change_description}} |

### Tests Added

| Test | Description | File |
| --- | --- | --- |
| TC{{test_id}} | {{test_description}} | {{test_file}} |

---

## Verification

- [ ] Fix verified in development
- [ ] Regression tests pass
- [ ] No side effects observed
- [ ] **Mutation-checked** - the regression test was seen to **fail** against the unfixed code (re-introduce the bug → test red → restore), proving it actually pins the fix. Record: `{{mutation_check_note}}`

**Verified by:** {{verifier}}
**Verification date:** {{verification_date}}
**Verification depth:** {{verification_depth}}

> Verification depth tiers: `smoke` (one-shot ping) | `functional` (single round-trip) | `conversational` (multi-turn / multi-step) | `soak` (live traffic over a window) | `live` (operator-confirmed in production with no rollback). See `reference-test-best-practices.md#verification-depth-tiers`. A bug cannot be marked **Fixed** until depth is at least `functional`; promoting **Fixed** to **Verified** requires a tier ABOVE functional (`conversational`/`soak`/`live` - Verified claims the higher-tier proof landed). A production-affecting bug (declare it with a `> **Production-affecting:** yes` header field) cannot be **Closed** until depth is at least `soak` (default 7 days). **These tiers are enforced**: `transition.py` refuses a Fixed/Verified/Closed transition that under-shoots them (a missing depth field is refused, not assumed) - `--force` records an override.
>
> **The regression test must be mutation-checked** (above): a test added alongside a fix but never seen to fail may be asserting the wrong thing and would not catch the bug's return. Seeing it red against the unfixed code is the proof it pins the fix. See `reference-test-best-practices.md#mutation-check`.

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| {{created_date}} | {{reporter}} | Bug reported |
