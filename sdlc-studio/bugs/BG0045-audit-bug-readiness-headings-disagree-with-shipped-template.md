# BG0045: audit bug-readiness check disagrees with the shipped bug template, so every template-authored bug flags "underspecified"

> **Status:** Closed
> **Created:** 2026-07-04
> **Created-by:** field report (a consuming project's sprint retro, 2026-07-04)
> **Severity:** medium

## Summary

`audit.py check` judges a bug ready only when the file contains the literal headings
`## Steps to Reproduce` **and** `## Proposed Fix` (`_bug_underspecified`, audit.py:79). The shipped
`templates/core/bug.md` uses `## Reproduction Steps` and `## Fix Description` instead. The two have
drifted: this repo's own dogfooded bugs use the check's vocabulary, but every downstream project that
authors bugs from the shipped template gets a false "underspecified" verdict on **every bug, forever** - regardless of how complete the repro and fix content is.

Field impact (a consuming project, 2026-07-04): a sprint tranche audit reported `0/4 ready` on four fully
specified bugs; the operator loop had to rule the verdicts false-positive in the decisions ledger and
proceed past its own deterministic gate. A readiness gate that mis-reports on its own template's
output is the LL0008 class (a deterministic tool must not report a state it did not verify) - still
present after the v3.3.0 update (empirically re-verified: `_bug_underspecified` returns `True` for
template-authored bugs with full repro + fix sections).

## Steps to Reproduce

1. Author a bug from `templates/core/bug.md` (headings `## Reproduction Steps`, `## Fix Description`),
   fully filled in.
2. Run `scripts/audit.py check --bugs Open` in that project.
3. The bug is reported `NOT READY ... underspecified` with the guidance "add Steps to Reproduce and a
   Proposed Fix" - which the file already has, under the template's own heading names.

## Proposed Fix

Two-part: (a) make `_bug_underspecified` accept both vocabularies - `("## steps to reproduce" in low or "## reproduction steps" in low) and
("## proposed fix" in low or "## fix description" in low)` - because released projects already carry
template-authored bugs that must not start flagging; (b) align `templates/core/bug.md` headings with
the canonical vocabulary (whichever is chosen) so the drift cannot recur, and add a unit test that
renders the shipped template and asserts `_bug_underspecified(rendered) is False` - the gate validated
against its own template's output (the LL0010 discipline). Sibling of [[BG0046]] (a second
check-vs-shipped-template disagreement found in the same field run). CHANGELOG.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | field | Reported from a consuming project's sprint close (retro lesson 1) |
| 2026-07-04 | claude | Fixed: `_bug_underspecified` accepts both vocabularies; `templates/core/bug.md` aligned to the canonical `Steps to Reproduce` / `Proposed Fix`. Mutation-checked: the 3 new tests (template-vocab, mixed-vocab, render-the-shipped-template) were seen RED against the unfixed predicate before the fix. Verification depth: functional (unit + rendered-template regression; not production-affecting). |
