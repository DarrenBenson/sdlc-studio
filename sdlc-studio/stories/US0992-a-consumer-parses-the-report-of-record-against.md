# US0992: A consumer parses the report of record against a published, versioned annex

> **Status:** Draft
> **Delivers:** CR0609
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-evidence-schema.md, .claude/skills/sdlc-studio/reference-schema.md, .claude/skills/sdlc-studio/help/references.md, .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_report.py, changelog.d/US0992.md
> **Epic:** EP0275
> **Points:** 5
> **Depends on:** CR0610, US0991
> **Persona:** Maya Okafor

## User Story

**As** a team lead whose dashboard reads our committed sprint reports
**I want** the report of record's envelope, figure shape, source grammar and section catalogue published as a versioned annex that the suite holds to the reports the close files
**So that** a skill upgrade that changes the report either keeps my parser working or says what moved, instead of breaking it silently

## Acceptance Criteria

- **AC1:** Given a report filed by `sprint close` in a fixture run carrying every section (metered cost, a refusal log, a not-measured close item, a ruling and a waiver), when the conformance test parses the annex's catalogue tables by their headings and reads the report against them, then every envelope key, section key, figure key and row key the report holds is in those tables, and every section the tables mark always emitted is present.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_report.py::ReportAnnexTests::test_a_filed_report_conforms_to_the_annex
- **AC2:** Given two fixture runs closed through `sprint close`, one with a refusal log and a not-measured close item and one with neither, when the sections each filed page carries are compared with the annex's catalogue, then their union equals the catalogue, and the sections the bare run lacks are exactly those the catalogue marks conditional, each naming the condition under which it is absent.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_report.py::ReportAnnexTests::test_the_section_catalogue_matches_what_the_builder_emits
- **AC3:** Given the four schema-1 pages this repository holds (RPT0002-RPT0005), copied into a fixture, when the test reads their section and envelope keys and runs `sprint_report.py check` on each, then the union of their sections equals the annex's schema-1 catalogue with `waivers` marked optional and `window_end` an optional envelope key, and each check answers that the page stands as filed, as the annex says.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_report.py::ReportAnnexTests::test_schema_one_is_documented_as_it_stands

## Notes

- Release: 6.2 (D0355 breakdown G1, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: a section, figure key, row key or envelope rule mark added to build_report with no catalogue row (a mention in the annex's prose alone must not satisfy it), or a section marked always emitted that the builder stops emitting
- AC2 must fail on: an annex entry for a section the builder no longer emits, a conditional section documented as always present, or a new conditional section with no catalogue row
- AC3 must fail on: a schema-1 catalogue of the fifteen sections RPT0002 carries, leaving `waivers` undocumented; `waivers` marked required; or schema 1 documented as re-derivable
- Serves Jonah's End goal 4, 'Upgrade safely as the skill evolves' (jonah-reyes-team-lead.md:29).
- Measured yield for the conformance test (LL0056): the envelope gained `window_end` at RPT0003, `record_paths` at RPT0011, four keys at RPT0015 (token_ratio, restore_pairing, discharged_carry, findings_scan), four at RPT0016 (minutes_ratio, delegated_tokens, agent_minutes, dora_failures) and `findings_window_end` at RPT0017. Schema 2 carries 10 sections at RPT0006, 13 at RPT0010 (with the conditional `unmeasured`) and 12 at RPT0019. Each was a silent change to a consumer.
- Schema 1 is two shapes: RPT0002-RPT0003 carry 15 sections, RPT0004-RPT0005 carry 16, adding `waivers`. These pages are immutable and no writer can produce schema 1, so the committed pages are the only source.
- Schema-2 sections at HEAD: goal, estimates, delivered, known_issues, signoff (FRONT_PAGE, sprint_report.py:3293); cost, dora, calibration, rulings, waivers, lane_yield, lessons (APPENDIX, :3294); unmeasured. lane_yield is absent without a refusal log, and unmeasured when the close recorded none.
- The annex documents the source grammar a consumer meets: sources joined by ', '; the declared non-path sources (NON_PATH_SOURCES, sprint_report.py:4232); and workspace paths that may not exist yet, such as a ledger nothing has written to (`_source_resolves`, :4239).
- The fixture says 'metered cost' so the story stands if CR0610's money story is deferred; if that story lands first, its money keys appear in the fixture and must be documented, and the depends-on entry naming it is dropped if it is deferred.
- The JSON is of record; the Markdown twin and the HTML are renderings and stay uncontracted. reference-schema.md's Scope paragraph (lines 40-44) promises 'a future separately versioned annex'; point it at the new file. Consuming-facing reference style: no internal ids (RPT, D, BG) in the annex text. help/references.md is regenerated by `docgen.py references`, not hand-edited.
- The annex is versioned independently of the skill, starting at 1.0 (panel answer to Q5): skill minors move for reasons that change no evidence shape.
- Build first in this epic.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G1 after the refine panel's review |
