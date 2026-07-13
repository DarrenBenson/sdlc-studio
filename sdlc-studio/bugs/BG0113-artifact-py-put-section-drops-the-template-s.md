# BG0113: artifact.py _put_section drops the template's ### subsection prompts when a field is supplied

> **Status:** Open
> **Target:** v4.1
> **Severity:** Low
> **Created:** 2026-07-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Sam Eriksson; persona; v1

## Summary

Found by the BG0108 review (2026-07-13), non-blocking. `_put_section` replaces a section's body up to the next ##, so ### subsections under the target heading are removed when the caller supplies that field. Two templates affected: --fix on a bug drops the template's '### Files Modified' / '### Tests Added' prompts, and --option on an RFC drops the '### Option A' scaffold. Reproduced: '## Proposed Fix' renders as the supplied text with those subsections gone, validator clean. This loses SCAFFOLD PROMPTS, not caller content - strictly better than the pre-BG0108 behaviour of dropping the caller's words entirely, and it violates no AC - but an agent filling in a bug loses two useful prompts it would otherwise have been guided by.

## Steps to Reproduce

1. artifact.py new --type bug --title t --template full --fix FIXTEXT. 2. Open the artefact: '## Proposed Fix' contains FIXTEXT, and the template's '### Files Modified' and '### Tests Added' subsections are gone.

## Proposed Fix

Preserve ### subsections beneath a replaced ## heading: `_put_section` should replace only the prose body above the first ###, or re-append the template's subsections after the supplied content.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-13 | audit | Filed |
