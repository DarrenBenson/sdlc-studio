# US0842: consult yield is measured - findings per consult and the share folded or filed - so the requirement is revisited on evidence

> **Status:** Draft
> **Delivers:** RFC0058
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/consult.py, .claude/skills/sdlc-studio/scripts/tests/test_consult.py
> **Epic:** EP0256
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** operator deciding whether the consult requirement keeps its place
**I want** findings per consult and the share folded or filed, with anti-persona findings counted apart
**So that** the requirement is revisited on measured yield rather than on how the last consult felt

## Acceptance Criteria

Two decisions this story sits on are OPEN, and the criteria state what they assume rather than
settling them. D6 - how yield is measured and when the requirement is revisited - is open, so this
story ships the MEASUREMENT and no threshold, and the report passes no judgement. D5 - persona
validity - is open, so the number cannot separate "consults work" from "these three personas were
well written", and the tool says so in its own output rather than leaving a reader to infer it. All
counting is over US0840's parsed rows; this story adds no reading of its own.

### AC1: findings and disposition shares are counted from the dispositions table, once per finding

- **Given** a fixture consult whose dispositions table holds seven finding rows across FOLD, FILE, DECLINED and OPERATOR RULING OWED, and whose objections sections raise two of those findings twice, once per persona
- **When** `consult.py yield --root <fixture>` runs through `main`
- **Then** it reports seven findings, not nine, and the count and share of each of the four dispositions, each share printed beside the finding count it was computed over; and the same command over the real `sdlc-studio/reviews/consult-*.md` corpus returns a figure per artefact and exits 0
- **Mutant:** count findings from the objection bullets rather than the dispositions table - a finding two personas raised is counted twice, the folded share falls, and the requirement is judged on a number its own renderer inflates
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_consult.py::ConsultYieldTests::test_findings_and_disposition_shares_are_counted_from_the_dispositions_table

### AC2: anti-persona findings are counted apart, never folded into the headline

- **Given** a fixture consult of seven findings whose raiser column names the Negative persona on three, two of those correctly DECLINED, and the Primary and Secondary personas on the other four
- **When** yield runs
- **Then** it prints two figure sets - all personas, and Negative alone - each carrying its own findings count and folded-or-filed share, and the two are never summed into a single share
- **Mutant:** report one merged share - a persona whose structural role is to say no, and whose no is correctly declined, then depresses the very number the requirement is judged on, so the consult looks least useful exactly where it is working as designed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_consult.py::ConsultYieldTests::test_anti_persona_findings_are_counted_separately

### AC3: the report names the limit D5 leaves open, in both renderings

- **Given** any consult corpus
- **When** yield runs, once as text and once with `--format json`
- **Then** both carry a statement that the figures measure these personas as authored rather than consults in general, and that persona validity is unsettled - as a line beside the figures in the text rendering and as a field in the JSON, so bypassing the human rendering does not drop the caveat
- **Mutant:** print the figures alone - the yield then reads as evidence about consults when it is evidence about three cards, and the requirement is retired or entrenched on the wrong grounds
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_consult.py::ConsultYieldTests::test_the_persona_validity_limit_is_carried_in_both_renderings

### AC4: it states figures and passes no verdict, because D6 has ruled no threshold

- **Given** two fixture corpora, one whose findings are all FOLD or FILE and one whose findings are all OPERATOR RULING OWED
- **When** yield runs over each
- **Then** both exit 0, both print their figures, and neither output carries a verdict on them - no pass, fail, healthy, sufficient, below or above wording, and no threshold value anywhere
- **Mutant:** hard-code a threshold and print a verdict against it - a number nobody ruled becomes the decision on whether the requirement survives, which is precisely what D6 is open to settle
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_consult.py::ConsultYieldTests::test_the_report_states_figures_and_passes_no_verdict

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
