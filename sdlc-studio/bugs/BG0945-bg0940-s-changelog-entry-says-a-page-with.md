# BG0945: BG0940's changelog entry says a page with a late ruling is signed, though sign refuses until the run is re-closed

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** changelog.d/BG0940.md
> **Created:** 2026-10-05
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-05T07:47:09Z

## Summary

Found by the QA review of BG0940 (qa-s12-bg0940, RUN-01M45FV6), filed under D0338. changelog.d/BG0940.md says the filed page 'still checks VALID when it is signed', but through the CLI the ruling's decisions.md row trips sign's existing tree check (sign REFUSED: sdlc-studio/decisions.md), so the run cannot be signed without a re-close, and the re-filed page still omits the withheld ruling. The VALID half is true; the sign half over-claims.

## Steps to Reproduce

In a fixture: sprint close, decisions.py add --by operator, sprint sign: refused naming sdlc-studio/decisions.md.

## Proposed Fix

Reword the fragment to what happens: the page stays VALID, sign refuses the changed tree as before, and a re-close files a page that does not count the late ruling.

## Acceptance Criteria

- [ ] **AC1** Given changelog.d/BG0940.md, then it no longer says the page is signed after a late ruling, and it says sign refuses the changed tree until a re-close. Fails on: the current 'still checks VALID when it is signed' wording
  - **Verify:** shell ! grep -q 'still checks VALID when it' changelog.d/BG0940.md && grep -q 're-close' changelog.d/BG0940.md

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-05 | sdlc-studio | Filed |
