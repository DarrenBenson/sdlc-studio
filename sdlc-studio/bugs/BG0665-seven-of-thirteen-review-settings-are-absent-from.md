# BG0665: seven of thirteen `review.*` settings are absent from the file that calls itself the single source of truth, and two of them are named in refusals users hit

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_config.py
> **Evidence:** 2026-09-11 sweep of every `"review.<key>"` literal in the shipped scripts against `templates/config-defaults.yaml`, `reference-config.md` and `help/`: 13 keys read, 6 declared in the defaults, 7 absent. Of the 7, `test_plan_after` and `two_role_after` are quoted back to the user in `transition.py`'s refusals.
> **Created:** 2026-09-11
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`config.py` documents `templates/config-defaults.yaml` as the single source of truth for skill defaults. Measured against the keys the shipped code actually reads, seven of thirteen `review.*` settings appear in it nowhere: `test_plan_after`, `two_role_after`, `line_coverage_after`, `signoff`, `blocking_priority`, `require_brief_provenance` and `max_rounds`.

Two of those are NAMED TO THE USER in a refusal. The `transition` command tells a reader that the unit has no Test Plan section and that `review.test_plan_after` puts it in scope, and separately that the unit is past `review.two_role_after`. A user told which setting put them in scope, who then looks that setting up, finds nothing - not in the defaults, not in `reference-config.md`, not in any help file. v5.1 widened when the first of those fires (BG0630), so the refusal is reached more often than before.

The two also take DIFFERENT KINDS OF VALUE despite the matching `_after` suffix: `test_plan_after` is a DATE compared against the unit's `Created` field as a string, and `two_role_after` is an ID CUTOFF parsed by `parse_cutoff`, which accepts `57` or `US0103` and raises on anything else. Guessing wrong gets a loud failure from one and silent scope changes from the other.

## Steps to Reproduce

1. Trigger the gate: transition a unit created after the cutoff with no `## Test Plan`.
2. Read the refusal - it names `review.test_plan_after` as the reason.
3. Look the key up: `grep -rn test_plan_after` over every shipped `.md` and `.yaml` returns nothing outside the scripts.
4. Repeat for `review.two_role_after`, and for the five other keys the code reads.

## Proposed Fix

Declare every `review.*` key the code reads in `templates/config-defaults.yaml` with its default, its accepted values and what it costs, and extend `reference-config.md`'s Review Configuration section to match. State explicitly that `test_plan_after` takes a DATE and `two_role_after` takes an ID, because the shared suffix invites the wrong guess. `max_rounds` stays absent - that is a recorded decision - but the file should SAY it is deliberately absent, or the next reader files this bug again. Pin it with a test that derives the key set from the code rather than listing it, so the next key added is caught.

## Acceptance Criteria

- [ ] **AC1** Given every `review.*` key the shipped scripts read, when the defaults file is checked against them, then each key is declared there with its default. Derived from the code rather than from a list, so the next key added is caught rather than exempted by an inventory nobody updated
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_config.py::ReviewKeysAreDeclaredTests::test_every_review_key_the_code_reads_is_declared_in_the_defaults
- [ ] **AC2** Given `review.test_plan_after` and `review.two_role_after`, when their documentation is read, then it states that the first takes a DATE compared against `Created` and the second takes an ID cutoff - the shared suffix is exactly what makes the wrong guess natural, and one of the two raises on a date while the other silently accepts an id-shaped string
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_config.py::ReviewKeysAreDeclaredTests::test_the_two_cutoffs_document_the_kind_of_value_each_takes
- [ ] **AC3** Given `review.max_rounds`, which is deliberately absent, when the defaults file is read, then its absence is stated with the reason. The paired control: an unexplained absence is indistinguishable from an oversight, and the obvious repair is to add the key back - which is the thing a recorded decision forbids
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_config.py::ReviewKeysAreDeclaredTests::test_a_deliberately_absent_key_says_so

## Impact

A gate refuses, names the setting that caused it, and the setting is undocumented. That is the worst shape a refusal can take: the user is given a lead that goes nowhere, and the cheapest way out is to stop using the gate. It lands hardest on a consuming project, which has neither this repository's history nor its decision log.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `.claude/skills/sdlc-studio/templates/config-defaults.yaml`, delete the `blocking_priority` declaration from the review block | Every key the code reads is declared |
| AC2 | in `.claude/skills/sdlc-studio/templates/config-defaults.yaml`, strip the DATE wording from the `test_plan_after` comment | Each cutoff states the kind of value it takes |
| AC3 | in `.claude/skills/sdlc-studio/templates/config-defaults.yaml`, delete the note recording why `max_rounds` is absent | A withheld key is told apart from a forgotten one |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-11 | Claude Opus 5 | Filed |
