# BG0048: provenance remake mass-backfills artifacts the adopt_after cutoff exempts, and double-stamps a non-tool Created-by

> **Status:** Closed
> **Verification depth:** functional (unit tests: cutoff exemption, --all override, no-double-stamp, field Created-by accepted)
> **Severity:** low
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio file

## Summary

Two related defects in provenance.py, hit during the 2026-07 project upgrade. (1) 'check' honours the provenance.adopt_after cutoff (2 unstamped reported), but 'remake' ignores it and stamped all 145 artifacts - contradicting reference-upgrade.md's stated intent that existing artefacts are exempt, not mass-stamped; the operator had to git-checkout 143 files back. (2) An artifact whose Created-by carries a legitimate non-tool value (e.g. 'field report (a consuming project...)') is counted un-stamped by check, and remake then ADDS a second Created-by line rather than recognising or replacing the existing one - CR0139 briefly carried two Created-by fields.

## Steps to Reproduce

1. In a repo with provenance.adopt_after set and artifacts predating it, run provenance.py check (reports only post-cutoff unstamped). 2. Run provenance.py remake. 3. All pre-cutoff artifacts are stamped too. 4. Separately: give an artifact 'Created-by: field report (...)' and run remake - a second Created-by line is appended.

## Proposed Fix

remake takes the same adopt_after exemption as check (opt out via an explicit --all flag); when a Created-by line already exists, remake either recognises a non-tool value as provenance (and leaves it) or replaces the line in place - never appends a duplicate field. Unit tests pin both.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | audit | Filed |
| 2026-07-04 | claude | Fixed: remake honours adopt_after (opt out with --all); ANY non-empty Created-by counts as provenance for both check and remake, so a field-report attribution is never nagged or double-stamped. Mutation-checked: 4 new tests seen RED against the unfixed module. |
