# BG0114: the documented conformance stage has no remediation hint, and the guard meant to catch that is blind to it

> **Status:** Open
> **Severity:** Medium
> **Created:** 2026-07-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Dani Okafor; persona; v1

## Summary

Found while delivering CR0235 (2026-07-13). The 'documented' conformance stage can appear in a unit's 'missing' list, but it has NO entry in the REMEDIATION registry - so an operator told their unit is non-conformant on 'documented' gets no guidance on what to do about it. Worse, the guard test written to catch exactly this class, `test_registry_covers_every_emitted_finding_kind`, passes only because its hardcoded 'expected' set ALSO omits 'documented'. The test and the registry share the same blind spot, so the guard certifies a gap it was written to prevent. This is the LL0008 false-assurance class: a check that reports success it did not achieve.

## Steps to Reproduce

1. grep the REMEDIATION registry in lib/`sdlc_md.py` for 'documented' - absent. 2. Read `test_registry_covers_every_emitted_finding_kind`'s hardcoded expected set - 'documented' is absent there too. 3. The guard passes.

## Proposed Fix

Add a remediation hint for 'documented'. Then fix the guard so it cannot share the registry's blind spot: derive the expected set from the stages conformance can actually emit, rather than hardcoding it - a guard that is handed its own answer key is not a guard.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-13 | Dani Okafor | Filed |
