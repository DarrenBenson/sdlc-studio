# BG0079: v4 rc-readiness checklist omits the eval gate its own release-gate template mandates; evals last ran at v3.5.0

> **Status:** Fixed
> **Severity:** Medium
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file
> **Verification depth:** functional (the four scenarios actually re-run via the two-Claude loop, 4/4 PASS with independent graders; checklist row present with the run recorded)

## Summary

rc-verdict: BLOCKS v4.0 tag. templates/workflows/release-gate.md:29-31 (any failed blocking behaviour blocks the tag) and :100-101 ('Eval scenarios re-run for the new major', shipped in this release) both require an eval run; sdlc-studio/reviews/v4-rc-readiness.md:10-18 has no eval row and reads 'GREEN on the rc gates'. The evals last ran in full at v3.5.0; v3.6.0 skipped with a recorded rationale; the 4.0.0 CHANGELOG entry, RETRO0016 and the checklist contain no eval record - and CHANGELOG v3.5.0 mandates a scenario-01 re-run after any SKILL.md description change, which commit fa74cd4 made after v3.5.0. The checklist is billed as 'a checklist read, not a judgement call' while missing a gate two of its governing documents require. Found by RV0007.

## Steps to Reproduce

grep -ci eval sdlc-studio/reviews/v4-rc-readiness.md -> 0; compare templates/workflows/release-gate.md:29-31 and :100-101; git log --oneline v3.5.0..HEAD -- .claude/skills/sdlc-studio/SKILL.md shows the description change.

## Proposed Fix

Add an 'Eval scenarios re-run' row to v4-rc-readiness.md; run the four scenarios per evals/README.md before the tag and record results.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
