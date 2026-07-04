# BG0050: file_finding doubles the AC checkbox when the caller supplies one

> **Status:** Closed
> **Verification depth:** functional (regression: boxed/ticked/bare inputs; mutation-checked RED against the unfixed renderer)
> **Severity:** low
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio file

## Summary

The CR renderer prepends '- [ ]' to every --ac value unconditionally, so an AC passed with its own leading checkbox (the natural way to paste one) renders as '- [ ] - [ ] text'. All seven CRs of the 2026-07 dogfood write-up (CR0143-CR0149) shipped malformed - found by the operator's adversarial review, with the note that a CR about tool-authoring gaps was itself malformed by the tool that authored it.

## Steps to Reproduce

1. file_finding.py file --type cr ... --ac '- [ ] already boxed'. 2. Open the created CR: the AC line reads '- [ ] - [ ] already boxed'.

## Proposed Fix

Normalise in the renderer: strip a leading '- [ ]'/'-[x]' from each supplied AC before prepending the canonical checkbox (idempotent for bare text). Regression test pins boxed, ticked-variant, and bare inputs.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | audit | Filed |
| 2026-07-04 | claude | Fixed: the CR renderer strips a supplied leading checkbox before prepending the canonical one (idempotent). The seven affected CRs (CR0143-0149) repaired. Test seen RED against the unfixed renderer, GREEN after. |
