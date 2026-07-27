# BG0332: Test scope pinned to a 58-script inventory when the tier ships 70

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** sdlc-studio/tsd.md
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

Both specs define the script-tier surface as 58 scripts while scripts/ contains 70 top-level helpers; because the TSD concedes no sweep enforces per-script coverage, this pinned count is the only inventory bounding the unit-test scope and it is ~17% short, in documents whose stated rule is not to pin drifting numbers.

## Steps to Reproduce

Evidence (In Scope line 67 and Test Organisation line 616; same figure in prd.md line 94): tsd.md:67 and :616-617 plus prd.md:94-95 pin 58; ls .claude/skills/sdlc-studio/scripts/*.py | wc -l returns 70; tsd.md:220-222 concedes the absence of an enforcing sweep.

## Proposed Fix

Replace the pinned 58 with the current count or unpinned wording ('the shipped helpers under scripts/') in both tsd.md and prd.md.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
