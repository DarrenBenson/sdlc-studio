# US0358: the report distinguishes a pre-existing failure from one the change introduced

> **Status:** Draft
> **Delivers:** CR0348
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0123
> **Points:** 3
> **Affects:** tools/lint_corpus.py, tools/tests/test_lint_corpus_attribution.py, .github/workflows/lint.yml

## User Story

**As a** contributor whose change is blocked by a corpus lint failure
**I want** the report to say which findings my change introduced and which were already there
**So that** I fix what I broke and the rest is attributed to the commit that actually introduced it, instead of to whoever next touched the file

## Acceptance Criteria

### AC1: Every finding is classified against the baseline revision

- **Given** a corpus run with a baseline revision to compare against (the merge base, or an explicit ref)
- **When** the same enumeration and rule set are run at the baseline and the two finding sets are compared
- **Then** a finding present at the baseline is reported as pre-existing and one absent there is reported as introduced, with the counts of each named in the summary line
- **Verify:** pytest tools/tests/test_lint_corpus_attribution.py::AttributionTests::test_a_finding_absent_from_the_baseline_is_reported_as_introduced
- **Verified:** yes (2026-07-24)

### AC2: Line drift alone does not reclassify a pre-existing finding

- **Given** a pre-existing finding whose line number moved because unrelated content was inserted above it
- **When** the two finding sets are compared
- **Then** it is still reported as pre-existing, because a finding is fingerprinted by file, rule id and offending text rather than by line number
- **Verify:** pytest tools/tests/test_lint_corpus_attribution.py::AttributionTests::test_line_drift_alone_does_not_reclassify_a_pre_existing_finding
- **Verified:** yes (2026-07-24)

### AC3: A baseline that cannot be read reports unattributed, never pre-existing

- **Given** a shallow clone, a missing merge base or a baseline checkout that fails
- **When** the corpus lane runs
- **Then** every finding is reported as unattributed and the report says the baseline could not be read, so no finding is quietly forgiven as pre-existing
- **Verify:** pytest tools/tests/test_lint_corpus_attribution.py::BaselineDegradationTests::test_an_unreadable_baseline_reports_unattributed_rather_than_pre_existing
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed: real ACs + Affects authored |
| 2026-07-24 | sdlc-studio | Built TDD: baseline attribution by text fingerprint, counted not set-based; 3 ACs green, mutation-proven |
