# BG1307: The shipped persona registry reader parses only the Primary, Secondary and Negative headings of `personas/index.md`, so a Served persona such as RFC0063's change approver is invisible to `status` and `hint`

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Evidence:** lib/sdlc_md.py:2768 docstring and the refusal at :2814 name only Primary/Secondary/Negative; the run nine product seat's grooming report
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T12:38:31Z

## Summary

Found by the product seat grooming CR0689 for run nine (2026-11-09). The registry reader in `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py` (around line 2768) parses `sdlc-studio/personas/index.md` into Primary, Secondary and Negative only, although the persona guide declares six cast roles including Served and Customer. When US1147 adds Graham Doyle under a Served heading (RFC0063 D3, D0437), `status` and `hint`, which read the registry through it, will not see him, and a consuming project with a Served or Customer persona has the same gap.

## Steps to Reproduce

1. In a scratch project, add a `## Served` heading to `sdlc-studio/personas/index.md` with one card listed under it.
2. Run the shipped status command against that project.
3. The Served persona is not reported; only the Primary, Secondary and Negative entries are.

## Proposed Fix

Read every cast role the persona guide declares (Primary, Secondary, Supplemental, Negative, Customer, Served) from the index, keep the existing roles' behaviour, and add a test that a Served entry is returned beside a control index holding only the three current roles.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Found by the product seat grooming CR0689 for run nine (2026-11-09).
- [ ] **AC2** The proposed fix lands, pinned by a test: Read every cast role the persona guide declares (Primary, Secondary, Supplemental, Negative, Customer, Served) from the index, keep the existing roles'...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
