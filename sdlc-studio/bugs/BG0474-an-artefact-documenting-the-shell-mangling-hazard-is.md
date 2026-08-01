# BG0474: An artefact documenting the shell-mangling hazard is flagged as a casualty of it, so the defect cannot be written about

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_shell_hazard_rate.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The shell-hazard detector flags an artefact field carrying the fingerprints of command substitution: an unbalanced backtick, a dollar-paren, and a collapsed double space where a removed token's flanking spaces closed up. It cannot distinguish a field the shell mangled from a field DESCRIBING that mangling, so an artefact filed about the hazard reproduces its evidence and is flagged as a victim of it.

Hit while filing CR0516, which reports that review-batch has no fields-file and therefore loses backtick-quoted terms from a findings string. Quoting the before-and-after - the only honest way to show what was lost - put a genuine collapsed double space into the artefact, and `test_no_legitimate_artefact_field_is_flagged` went red over the whole repository. The workaround was to describe the mangling in words rather than reproduce it, which makes the report weaker than the evidence it is reporting.

Distinct from BG0301 (Fixed), which was aligned code-block spacing. This shape is a legitimate field quoting the hazard, and it will recur for anyone documenting it - including the fix for CR0516 itself, whose own tests must contain exactly these strings.

## Steps to Reproduce

1. Write a CR whose summary quotes a mangled findings string, including the two spaces left where the removed token stood.
2. Run pytest over `test_shell_hazard_rate.py.`
3. `test_no_legitimate_artefact_field_is_flagged` fails, naming the CR and the collapsed-double-space signature. The sample is the whole tracked corpus, so one documenting artefact reddens a repo-wide guard.
4. Reword the quotation into prose and the suite returns green - the evidence removed rather than the defect fixed.

## Proposed Fix

Give the detector an exemption the artefact declares, in the shape this repo already uses for a recorded exception rather than a blanket skip: a field or fenced region marked as QUOTING the hazard is sampled but not flagged, and the marker is visible so a reader can tell a documented example from a live casualty. A blanket path allowlist is the wrong instrument - it would exempt real mangling in the same file. The guard must stay able to fail on a genuine casualty sitting beside a quoted one, which is the control any fix needs.

## Acceptance Criteria

- [ ] The behaviour described is corrected: The shell-hazard detector flags an artefact field carrying the fingerprints of command substitution: an unbalanced backtick, a dollar-paren, and a collapsed...
- [ ] The proposed fix lands, pinned by a test: Give the detector an exemption the artefact declares, in the shape this repo already uses for a recorded exception rather than a blanket skip: a field or...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Filed |
