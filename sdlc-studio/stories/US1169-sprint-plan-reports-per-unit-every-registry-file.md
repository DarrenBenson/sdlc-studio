# US1169: sprint plan reports, per unit, every registry file its new script, verb or flag implies, and every page threshold it nears, that its Affects omits

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0705
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_plan_registry_advisory.py, changelog.d/US1169.md
> **Epic:** EP0313
> **Points:** 5
> **Depends on:** US1165
> **Persona:** Abena Osei

## User Story

**As a** head of engineering whose teams take changes through a change board
**I want** sprint plan reports, per unit, every registry file its new script, verb or flag implies, and every page threshold it nears, that its Affects omits
**So that** I know what each team's delivery costs per point and can hold it to a monthly budget

## Acceptance Criteria

- **AC1:** Given a unit whose Affects names a not-yet-existing `.claude/skills/sdlc-studio/scripts/<name>.py`, when `sprint.py plan` runs, then it reports each registry that new script implies and the Affects omits: sdlc-studio/reviews/root-census.md, a reference-scripts page for its `### <name>.py` heading, reference-scripts-surface.md, sdlc-studio/reviews/command-audit.md, and lib/surface.py when the script has no parser.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_registry_advisory.py::PlanRegistryAdvisoryTests::test_a_new_script_names_its_registries
- **AC2:** Given a unit whose criteria name `<script>.py <verb>` for a verb that script's parser does not expose, or a `--flag` it does not take, when the plan runs, then it reports reference-scripts-surface.md and sprint_report.py (NON_CEREMONY_VERBS) for the verb, command-audit.md for the flag, and scripts/tests/test_artifact.py when the flag is `--fields-file` or the script is a free-prose writer; a verb or flag the parser already has is not reported.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_registry_advisory.py::PlanRegistryAdvisoryTests::test_a_new_verb_or_flag_names_its_registries
- **AC3:** Given a unit whose Affects names a reference page within 20 lines below the 400-line reading-guide threshold, past 600 lines with no ALLOWLIST entry, or within 10 lines of its ALLOWLIST ceiling plus 5%, when the plan runs, then it reports the threshold, the page's size and the file to add (the regenerated guide, or tools/check_budgets.py).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_registry_advisory.py::PlanRegistryAdvisoryTests::test_a_page_near_a_threshold_names_the_guide_or_ceiling
- **AC4:** Given the same units with the implied files in their Affects, and a consuming project whose tree has none of these registries, when the plan runs, then it reports nothing for them and never refuses the plan.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_registry_advisory.py::PlanRegistryAdvisoryTests::test_a_unit_naming_its_registries_or_a_consuming_project_is_clean

## Notes

- Serves Abena Osei's End goal 3; delivers part of CR0705 (D0479).
- AC1 must fail on: a unit adding a script with only the script and its test in Affects reported clean
- AC2 must fail on: an existing verb reported (false positive), or a new flag pointed at the unjudged-flags baseline, which only shrinks
- AC3 must fail on: a 395-line page, or reference-config.md at 729 lines against 695 plus 5%, reported clean
- AC4 must fail on: the advisory refusing a plan, or naming skill-repository registries in a consuming project
- Start from sprint.py `affects_mismatch` (:894, advisory by construction, D0053), `affects_findings` (:4107) and `_affects_files` (:814). Thresholds: docgen.GUIDE_THRESHOLD (docgen.py:49) and long_references (:266); the ALLOWLIST is repo-only (tools/check_budgets.py), so read it only where it exists.
- Run twelve lost five lands and run thirteen two to these registries (CR0705 evidence; BG1459). Found again in grooming: reference-config.md is at its ceiling now, so CR0699-A pays for it.
- Shares sprint.py and test_sprint.py with CR0699-A, which lands in wave 1; this builds in wave 2.
- The new test carries `# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-15 | Claude Opus 5.5 (run fourteen grooming, D0479) | Groomed: criteria with Verify lines, must-fail notes, Affects with the tests each change exercises and this unit's fragment |
