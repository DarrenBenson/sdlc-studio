# BG0161: Accepted-and-delivered RFCs 0018, 0022 and 0023 still list every design decision as Open, with leanings contradicting the recorded outcomes and no Decision sections

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** sdlc-studio/rfcs/RFC0018-self-check-candidates-vocabulary-consistency-verb-taxonomy-and.md, sdlc-studio/rfcs/RFC0022-portable-mutation-check-gate-fault-injection-across-languages.md, sdlc-studio/rfcs/RFC0023-a-tolerant-convention-layer-retire-the-exact-string.md
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

Three instances of the same write-back failure, spanning June and July (systemic, not one lapse). RFC0022: decisions.md D0002 records 'D1-D6 settled... CR0134 unblocked and built', yet the RFC shows all six rows Open with no Decision section and a revision history ending its filing day. RFC0018: D0004 records C3 BUILT, C2 built, C1 DECLINED, yet the RFC shows all three Open with D1 'leaning defer' (declined - a different terminal outcome) and D3 'leaning defer' (built) - actively misleading on all three. RFC0023: D0010 records acceptance with 'D3 guard question resolved per-site', yet D1-D4 all read Open with the last revision predating acceptance. reference-rfc.md's accept flow requires no Open row and a filled Decision section before Accepted; the actual resolutions exist only in decisions.md rationale prose, while doctrine names the RFC as the living design home. All nine panel votes not-refuted. Mechanical paperwork fix.

## Steps to Reproduce

Open each RFC's Open Decisions table and compare with decisions.md D0002/D0004/D0010: every row still reads Open, RFC0018's leanings are the opposite of the disposition, no Decision sections exist, and no revision entry postdates acceptance.

## Proposed Fix

Write the outcomes back: mark each decision row with its resolution and a pointer to the D-entry and the shipped unit (e.g. RFC0022 D1-D6 per D0002/CR0134; RFC0018 C1 declined/C2-C3 built per D0004; RFC0023 D1-D4 per D0010 incl. the per-site guard); add Decision sections and revision rows.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Filed |
