# BG0172: test-specs/_index.md's 'Epics without specs' section is blank while 46 of 48 epics have no spec, and its Coverage/By-Test-Type tables are empty header-only shells

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** sdlc-studio/test-specs/_index.md
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

The test-spec index carries three derived sections asserting more than the census supports: 'Epics without specs:' is followed by nothing - reading as 'none' - when only TS0001 (EP0010) and TS0002 (EP0011) exist against 48 epics; 'Coverage Summary' and 'By Test Type' are tables with header rows and zero data rows; both listed specs read 'Automated: 0' with Status Ready. LL0013 applied to an index: the section that enumerates gaps silently exempts every gap it never computed, and the template's own semantics require omitting the header when the list is empty. Panel split 2-1 (the refuter noting this workspace's validation leg is the script suite, making specs dormant here - which supports a tidy-up, not inaction); reconcile passes it clean because it only syncs the Summary-by-Epic table. Low-severity honesty fix.

## Steps to Reproduce

Open sdlc-studio/test-specs/_index.md: Coverage Summary and By Test Type contain header rows only; 'Epics without specs:' is immediately followed by the next heading; compare with 48 epic files, 2 specs.

## Proposed Fix

Populate the derived sections (compute epics-without-specs, fill or remove the empty tables) or delete them per the template's omit-when-empty rule; optionally note that this workspace's validation leg is the script suite so the dormant sections stop implying full spec coverage.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Filed |
