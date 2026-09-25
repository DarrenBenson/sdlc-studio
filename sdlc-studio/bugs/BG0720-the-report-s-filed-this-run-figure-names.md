# BG0720: the report's Filed this run figure names the batch's delivered units as findings and omits a finding that was filed

> **Status:** Superseded
> **Closed with findings in:** D0273 v6 triage (Sprint 5, US0937), SUPERSEDED: US0875 (31ffb8fc) deleted `_carried_section`, so the report's filed-this-run figure now comes from the run record and the defective path no longer exists
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Created:** 2026-09-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

This is the class BG0458 closed, recurring one section further on: a row that reads the retro's PROSE where the record was available. BG0458 is Fixed and its repair stands; that is why the header figures are sound and this one is not.

Sharper still, US0835 AC2 is that rule stated as a criterion - 'the figures come from the run's artefacts, not from the retro's prose' - and its verifier checks the header counts, which do. `filed` sits in a different section, was never in the criterion's reach, and does exactly what the criterion forbids. The criterion's words outrun its fixture, which this project already names as its dominant review defect, and the run that shipped the rule is the run that broke it.

`_carried_section` derives the filed count with `actions = _table_rows(retro_text, 'Finding |')` and then regexes every BG/CR/US/RFC id out of those rows. On RETRO0118 that produced 'Filed this run: 10 - BG0706, US0832, US0833, US0834, US0835, US0836, US0837, US0844, US0845, US0846': all nine DELIVERED UNITS counted as findings this run filed, while BG0713 - which the run actually did file, and which sits in the retro's own carried table - is absent. The figure is wrong in both directions at once, and it is wrong in a way that flatters the run: nine units of delivered work are re-presented as nine findings raised. A reader comparing 'filed' against 'ruled' (2) on the same page cannot reconcile them, and the number is on the page a signature freezes.

## Steps to Reproduce

1. Close a run whose retro carries both a findings table and a per-unit cost table listing the batch's unit ids. 2. Read the report's 'Carried open' section. 3. 'Filed this run' names the unit ids from the cost table and misses findings listed only in the carried table. Observed on RPT0002 against RETRO0118: 10 named, 9 of them delivered units, BG0713 missing.

## Proposed Fix

Do not scrape ids out of whatever rows a loose header match returns. Derive the filed set from the artefacts themselves: a finding filed by this run is one whose `Raised-in-batch` names the run, which is the same source `_open_findings` uses and the field the filer writes. Failing that, bind `_table_rows` to the retro's findings table by its full header rather than a prefix, and assert in the test that a retro carrying a SECOND table of unit ids does not contribute to the count - that second table is what this defect is made of. Note BG0715 first: `Raised-in-batch` dating is itself unreliable for findings raised outside a delivery batch, so the two should be fixed together.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `_carried_section` derives the filed count with `actions = _table_rows(retro_text, 'Finding |')` and then regexes every BG/CR/US/RFC id out of those rows.
- [ ] **AC2** The proposed fix lands, pinned by a test: Do not scrape ids out of whatever rows a loose header match returns.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-19 | sdlc-studio | Filed |
