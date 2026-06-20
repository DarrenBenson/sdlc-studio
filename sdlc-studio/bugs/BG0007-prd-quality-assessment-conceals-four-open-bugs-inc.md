# BG-0007: PRD Quality Assessment conceals four open bugs (incl. a Critical) while overclaiming feature completeness

> **Status:** Open
> **Severity:** High
> **Reporter:** Project Audit
> **Date:** 2026-06-20
> **Epic:** --
> **Story:** --

## Summary

The PRD marks all features Complete [HIGH] and lists only two minor debts in §10, while four Open bugs (BG0003 Critical) sit in the same workspace; two feature ACs (Reconcile 'all artifacts', Verify AC 'Complete') are also factually wrong against the code those bugs document.

## Problem

prd.md:112 declares 'all features Complete ... Confidence [HIGH] - extracted directly from source', and §10 Technical Debt (prd.md:341-344) names only ID collisions and markdown validation. But bugs/_index.md records 4 Open bugs (BG0003 Critical, verify_ac AC parsing). Two ACs marked Complete [HIGH] are also false: Reconcile AC 'census of all artifacts' (prd.md:172) excludes bug/workflow types (reconcile.py:35 _DEFAULT_TYPES is six types, BG0002), and the Verify AC feature (prd.md:187) false-greens on bullet-style ACs because verify_ac.py:79 parses only ### AC headings (BG0003). The PRD's risk-disclosure section conceals risk.

## Proposed Fix

Add the four open bugs to §10 Technical Debt with severities and cross-reference bugs/_index.md. Change the Reconcile AC to 'Builds a census of indexed artifacts (story, epic, cr, rfc, plan, test-spec) from disk' to match reconcile.py. Annotate the Verify AC feature with a [MEDIUM] caveat referencing BG0003 (parser recognises only heading-style AC) until BG0003 is fixed.

## Evidence

prd.md:112 'all features Complete ... [HIGH]' vs bugs/_index.md (4 Open, BG0003 Critical) and reconcile.py:35_DEFAULT_TYPES (no bug/workflow) and verify_ac.py:79 AC_HEADING_RE sole AC trigger

## Impact

A reader trusting the PRD sees a clean all-Complete picture while a Critical release-gate defect and two overclaimed ACs hide in the same workspace; the section meant to disclose risk actively conceals it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Project Audit | Filed from the 2026-06-20 project-profile audit (lens: prd) |
