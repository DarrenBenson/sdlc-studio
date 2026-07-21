# BG0241: A test spec with no AC Coverage Matrix at all reports clean and exits 0

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Found and deliberately left in scope-declined state during BG0229, which fixed the adjacent case (a MISSING spec file read as an empty one and reported a clean matrix). The same vacuity family survives one step further in: a spec that is present, readable and valid UTF-8, but contains no AC Coverage Matrix section at all, still yields zero matrix rows and reports clean with exit 0. Absence of the section is indistinguishable from a section with nothing outstanding, which is the same defect BG0229 named - silence read as assertion integrity. Declined inside BG0229 because fixing it changes epic-ts semantics repo-wide, which is not a change to make mid-sprint on the way past; it earns its own unit, its own decision about what a spec with no matrix MEANS, and its own sweep of the specs that would newly fail.

## Steps to Reproduce

1. Take any test-spec file that is present and readable but has no AC Coverage Matrix section. 2. Run `verify_ac.py` ts-check against it. 3. Observe a clean report and exit 0, identical to the output for a spec whose matrix is complete. The two states are not distinguishable from the command's output or its exit code.

## Proposed Fix

Decide first what a spec with no matrix means - not yet written, deliberately not applicable, or malformed - because the three want different verdicts and only one of them is clean. Then make the absent-section case report distinctly from the complete-matrix case, the way BG0229 made the absent-FILE case exit 2 rather than 0. Before changing the default, sweep the existing specs to count how many would newly report, so the change lands as a known cost rather than a surprise red gate. Note the related guard already shipped: a vacuous verifier is refused per runner family, and a runner that ran nothing proves nothing whatever its exit code (L-0165).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
