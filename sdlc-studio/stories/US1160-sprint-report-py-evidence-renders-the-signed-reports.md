# US1160: `sprint_report.py evidence` renders the signed reports of record as one evidence table, and `--check` names a page that has drifted from them

> **Status:** Done
> **Risk-class:** standard
> **Delivers:** CR0702
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/reference-scripts-domain.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, sdlc-studio/reviews/command-audit.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py, .claude/skills/sdlc-studio/scripts/tests/test_docgen.py, .claude/skills/sdlc-studio/scripts/tests/test_evidence_page.py, changelog.d/US1160.md
> **Epic:** EP0310
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** head of engineering whose teams take changes through a change board
**I want** `sprint_report.py evidence` renders the signed reports of record as one evidence table, and `--check` names a page that has drifted from them
**So that** every release passes the change board on the evidence the run produced, with no separate write-up

## Acceptance Criteria

- **AC1:** Given a fixture of signed reports of record (one achieved, one partial with a verdict note, one holding a Dollars per point row and one without, two signed reports for the same run, and one unsigned report), when `sprint_report.py evidence --out <page>` runs, then the table between the page's generated markers has one row per run from that run's latest signed report, showing the goal verdict, a partial verdict's note, dollars per point where the report holds it and 'not recorded' where it does not, and the hours from `generated_at` to `signature.signed_at`; the unsigned report is left out.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_page.py::EvidencePageTests::test_one_row_per_signed_run_from_its_latest_report
  - **Verified:** yes (2026-11-15)
- **AC2:** Given a page with hand-written text outside its markers, when the verb regenerates it, then that text is left byte for byte, and every figure inside the markers traces to a named field of a committed report.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_page.py::EvidencePageTests::test_hand_text_is_kept_and_every_figure_is_a_report_field
  - **Verified:** yes (2026-11-15)
- **AC3:** Given a page whose table differs from the reports it names (a hand-edited cell), when `sprint_report.py evidence --out <page> --check` runs, then it exits 1 naming the run that differs; given a report signed after the newest report the page names, it exits 0 and prints that the run is not yet on the page.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_page.py::EvidencePageTests::test_check_names_a_drifted_run_and_only_notes_a_newer_report
  - **Verified:** yes (2026-11-15)
- **AC4:** Given the new verb and its flags, when the command registries are read, then `docgen.py surface --check` is clean, `sprint_report.NON_CEREMONY_VERBS` lists `evidence`, command-audit.md judges `--out` and `--check`, and the `### sprint_report.py` section of reference-scripts-domain.md names the verb.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_page.py::EvidencePageTests::test_the_verb_is_in_every_registry_a_new_verb_implies
  - **Verified:** yes (2026-11-15)

## Notes

- Serves Abena Osei's End goal 1 (also 3 and 5); delivers part of CR0702 (D0479).
- AC1 must fail on: a dollars figure computed from tokens and prices instead of read from the report, an unsigned report listed, or a run listed twice
- AC2 must fail on: the generator rewriting the hand-written explanation, or a figure with no report field behind it
- AC3 must fail on: --check exiting 0 on a hand-edited cell, or exiting 1 because a sprint close committed a newer report
- AC4 must fail on: any one of the four registries left without the verb or its flags
- Start from sprint_report.py build_parser (:6555) and NON_CEREMONY_VERBS (:886). Read reports through the keys reference-evidence-schema.md documents: goal.goal_verdict and goal.goal_verdict_note; the estimates rows whose est_measure is 'Dollars per point' (est_actual); top-level generated_at and signature.signed_at.
- Do not read the signoff section's principal or signed_at figures: all 29 signed reports hold 'not yet signed' there because the report is built before the sign (RPT0031.json); the top-level signature block is the record.
- At HEAD: 30 RPT*.json (RPT0002-RPT0031). RPT0004 is unsigned; RPT0017 and RPT0018 are both RUN-01M40TSJ; only RPT0027-RPT0031 hold Dollars per point ($2.89, $2.48, $2.22, $2.28, $2.27); RPT0002-RPT0005 hold no goal verdict.
- Reuse docgen's marker splice (docgen.find_region and splice, docgen.py:65-94) rather than writing a second marker parser.
- AC3's 'newer report' rule is a ruling for the orchestrator: without it every sprint close turns main red until someone regenerates the page. The release (run fifteen) regenerates it.
- Registries for a new verb: NON_CEREMONY_VERBS, reference-scripts-surface.md (regenerate with `docgen.py surface`), the existing `### sprint_report.py` heading in reference-scripts-domain.md (386 lines: stay under the 400-line guide threshold or regenerate its reading guide), command-audit.md for the flags. The unjudged-flags baseline only shrinks (tools/tests/test_baselines_only_shrink.py), so judge the flags; do not baseline them. Not a new script, so no root census or parser-coverage change.
- The new test module carries `# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-15 | Claude Opus 5.5 (run fourteen grooming, D0479) | Groomed: criteria with Verify lines, must-fail notes, Affects with the tests each change exercises and this unit's fragment |
