# CR-0327: Deterministic RFC decision paperwork: rfc resolve edits a decision row, and parent-aware CR filing wires both link directions at mint

> **Status:** Complete
> **Decomposed-into:** EP0061
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/rfc.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/artifact.py
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5; agent; RFC-triage retro 2026-07-17

## Summary

Two seams from the triage session, both mechanical: (1) `file_finding`/artifact gain --parent RFCxxxx (or CRxxxx) so a spawned child is minted with its Parent line AND the parent's Decomposed-into updated in one atomic call - reusing the link writers refine already moved into `lib.sdlc_md` (L-0051), so asymmetry cannot be created; (2) rfc.py gains resolve --rfc X --decision D2 --resolution 'text' [--refs CR0320] which edits the named decision-table row to Resolved with the text and refs and appends the revision row - the judgement stays the operator's, the table surgery stops being regex heredocs. Together they make the accept-by-derivation path (decide -> spawn -> deliver -> derive Accepted) fully tool-carried.

## Impact

The 2026-07-17 triage resolved 8 decision rows and wired 9 bidirectional links entirely by hand-rolled python heredocs; the missing Parent back-links produced 9 link-asymmetry drift items that a mint-time writer would have made impossible.

## Acceptance Criteria

- [ ] `file_finding` file / artifact new accept --parent <id>: the child is minted with Parent and the parent's Decomposed-into gains the child, atomically (validated before any write); reconcile shows no asymmetry immediately after
- [ ] rfc resolve edits exactly the named decision row (unknown RFC/decision refused loudly), records resolution text + refs + a revision row, and leaves other rows byte-identical
- [ ] reference-rfc.md documents decide -> resolve -> spawn as the triage ceremony

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 | Raised |
