# US0993: A consumer recomputes a report's fingerprint from the annex alone

> **Status:** Draft
> **Delivers:** CR0609
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-evidence-schema.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_fingerprint.py, changelog.d/US0993.md
> **Epic:** EP0275
> **Points:** 2
> **Depends on:** US0992
> **Persona:** Maya Okafor

## User Story

**As** the operator who signs the report of record
**I want** the fingerprint procedure stated in the annex precisely enough to recompute without the skill, and the annex to say plainly what the fingerprint does not cover
**So that** a dashboard can confirm a page is the one I signed without installing the skill, and nobody reads a figure's source as signed

## Acceptance Criteria

- **AC1:** Given the reference implementation the annex states for the schema-2 fingerprint, when the test extracts it and runs it with `python3 -I` from a temporary working directory with no skill scripts on the path, over a report filed by `sprint close` in a fixture and over the 14 committed schema-2 pages (RPT0006-RPT0019), then it returns the fingerprint each page records.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_fingerprint.py::FingerprintAnnexTests::test_the_annex_procedure_recomputes_filed_fingerprints_in_isolation
- **AC2:** Given the annex's lists of figures and sections left out of the digest, when they are compared with OUTSIDE_THE_DIGEST and SECTIONS_OUTSIDE_THE_DIGEST, then they are equal, and both the annex and reference-sprint.md state that the signature block, the generation time and each figure's source are not signed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_fingerprint.py::FingerprintAnnexTests::test_the_annex_exclusions_match_the_code

## Notes

- Release: 6.2 (D0355 breakdown G1, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: a reference implementation that imports sprint_report (it fails in isolation), or one that skips a branch of leaf_figures: the fixture carries section-level not_measured and no unit_rows, the committed pages carry unit_rows and no section-level not_measured, so only the two together catch either skip
- AC2 must fail on: a figure or section excluded from the digest in code with no annex line, or the unsigned-source statement missing from reference-sprint.md
- Serves Maya's End goal 2, 'Never lose the thread - know the true state of the work' (maya-okafor-founder-engineer.md:26).
- Delivers BG1007's option B, which the panel recommends: the second criterion is BG1007's 'state plainly that sources are not signed', in the annex and reference-sprint.md (see question 3 on the page itself). If the operator rules option A, this story depends on BG1007 and the second criterion and the reference implementation cover sources on pages carrying its rule mark.
- Verified at HEAD: today's algorithm (sprint_report.py:2837: sha256 of the ordered [section, key, value] list, compact JSON separators, ensure_ascii off, first 16 hex) recomputes all 14 committed schema-2 fingerprints. It does NOT recompute the schema-1 pages, so the annex states the procedure for schema 2 and says a schema-1 fingerprint stands as filed.
- The committed schema-2 pages are signed and immutable, so reading them does not carry the BG0955 and BG0957 coupling to live data (panel answer to Q2).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G1 after the refine panel's review |
