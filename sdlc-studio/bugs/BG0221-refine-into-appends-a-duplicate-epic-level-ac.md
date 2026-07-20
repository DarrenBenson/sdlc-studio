# BG0221: refine --into appends a duplicate epic-level AC heading that fails the repo's own markdown gate

> **Status:** Open
> **Severity:** Medium
> **Verification depth:** functional (pinned against the real markdownlint MD024 rule with the repo's own config, plus a local implementation of the rule so the pin holds without Node; both shown non-vacuous; merge dispatch deleted to re-introduce the defect and 5 tests failed)
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Refining a second request into an existing epic appends a second '## Acceptance Criteria (Epic Level)' section instead of merging under the one heading, so the epic immediately fails MD024 (no-duplicate-heading) in the pre-commit markdown lane. Observed on EP0092 (CR0369 then CR0371): the tool's own output blocked the commit that shipped it, and the operator had to hand-merge the sections.

## Steps to Reproduce

1. refine.py apply --request CRa --epic-title X --story 't|2' (multi-story, so ACs are carried to the epic). 2. refine.py apply --request CRb --into EPxxxx --story 't|2' --story 't2|3'. 3. Open the epic: two identical '## Acceptance Criteria (Epic Level)' headings. 4. git commit - the markdown lane fails MD024 on the epic.

## Proposed Fix

When --into carries request ACs to an epic that already has the epic-level AC heading, merge under the existing heading with a per-request subheading (e.g. '### From CRxxxx'), instead of appending a duplicate section.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Filed |
