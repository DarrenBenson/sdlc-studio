# BG0177: rfc decide misreports the drafts: ws counts a Workstream section no RFC has (never the Decomposed-into children), and decided RFCs still read READY for decision

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/rfc.py, .claude/skills/sdlc-studio/scripts/tests/test_rfc.py
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5; agent; RFC-triage retro 2026-07-17

## Summary

Observed live at the 2026-07-17 triage: after five RFCs gained 1-3 spawned CR children each (bidirectional Parent/Decomposed-into links, reconcile clean), rfc decide still printed ws=0 for every one - rfc.py:67 counts data rows of a '## Workstream' section table, a shape none of the 45 RFCs carries, and never consults Decomposed-into/`children_of`, the link model every other tool (transition's derivation gate, reconcile's asymmetry check) uses. LL0016: two code paths disagree on what a workstream IS, and the digest the operator reads is the wrong one. Second defect in the same output: RFCs whose every decision row is Resolved still flag READY-for-decision - the digest cannot distinguish undecided from decided-awaiting-delivery, so it invites re-deciding settled questions.

## Steps to Reproduce

1. Take an RFC with Decomposed-into: CRxxxx and children carrying Parent: back-links (e.g. RFC0044 after 260536c). 2. Run scripts/rfc.py decide. 3. Observe ws=0 despite the children, and READY on an RFC whose decisions are all Resolved.

## Proposed Fix

Count workstreams from `children_of` (the shared authority), falling back to the Workstream table for RFCs that use one; flag distinguishes UNDECIDED (open decision rows) from DECIDED-AWAITING-DELIVERY (all resolved, children not terminal) - the second must not read READY for decision.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 | Filed |
