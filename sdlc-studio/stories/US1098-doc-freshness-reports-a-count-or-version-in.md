# US1098: doc_freshness reports a count or version in the PRD or TSD that no longer matches the tree, as it does for the TRD

> **Status:** Done
> **Delivers:** CR0649
> **Created:** 2026-10-31
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/doc_freshness.py, .claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py, changelog.d/US1098.md
> **Epic:** EP0293
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer whose PRD and TSD state counts and versions
**I want** `doc_freshness.py` to report a count or version in the PRD or TSD that no longer matches the tree, as it does for the TRD
**So that** those two documents cannot drift for months between unified reviews unseen (LL0027)

## Acceptance Criteria

- **AC1:** Given a PRD stating a count the tree no longer holds, when `doc_freshness.py` runs, then it reports that PRD line with the stated and the derived figure
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py::PrdTsdFreshnessTests::test_a_stale_prd_count_is_reported
  - **Verified:** yes (2026-11-01)
- **AC2:** Given a TSD stating a baseline version or count the tree no longer holds, when it runs, then it reports that TSD line
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py::PrdTsdFreshnessTests::test_a_stale_tsd_figure_is_reported
  - **Verified:** yes (2026-11-01)
- **AC3:** Given a PRD and TSD whose figures match the tree or are stated as bands, when it runs, then neither document is reported (the positive control)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py::PrdTsdFreshnessTests::test_matching_prd_and_tsd_are_clean
  - **Verified:** yes (2026-11-01)

## Notes

- Serves: Maya Okafor, End goal 4 (specs never quietly drift from reality).
- AC1 must fail on: the PRD left out of the census's document set. AC2: the TSD left out. AC3: a band (`about 50`, `40+`) read as a pinned count and reported.
- Each derived figure is read from the tree by the census's existing derivations, never typed into the test.
- Risk: the live PRD and TSD carry stale figures today (RV0028 PRD and TSD legs), so the census will report them until US1102-US1104 land. If the doc-freshness lane blocks, landing this first turns the gate red; keep the lane's current severity for the two documents and say so in the fragment.
- Deliver first in run four, so US1102-US1104 are census-checked (CR0649 triage). Covers CR0649 AC1.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-31 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-31 | Claude Opus 5.5 | Groomed for run four (D0392): criteria with Verify lines, each criterion's mutant, overlaps and sequence |
