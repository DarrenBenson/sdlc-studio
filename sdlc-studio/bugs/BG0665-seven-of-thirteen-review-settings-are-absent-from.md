# BG0665: seven of thirteen `review.*` settings are absent from the file that calls itself the single source of truth, and two of them are named in refusals users hit

> **Status:** Fixed
> **Verification depth:** functional [[derived: criteria 3; plan rows 5; executed 5; killed 5; survived 0; not-run 0; entry point 0 of 3 criteria through the shipped CLI, 3 in-process | fp 8e0a079ad9b0 ]]
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
  - **Verified:** yes (2026-09-15)
- [ ] **AC2** Given `review.test_plan_after` and `review.two_role_after`, when their documentation is read, then it states that the first takes a DATE compared against `Created` and the second takes an ID cutoff - the shared suffix is exactly what makes the wrong guess natural, and one of the two raises on a date while the other silently accepts an id-shaped string
  - **Verify:** manual - retired by US0911: `review.test_plan_after` is deleted, so no DATE cutoff is left to tell apart from `review.two_role_after`
  - **Verified:** manual (2026-09-25) - retired, superseded by US0911
- [ ] **AC3** Given `review.max_rounds`, which is deliberately absent, when the defaults file is read, then its absence is stated with the reason, on both sides: no uncommented line declares `max_rounds:` as a live key, and the comment that mentions it gives the reason by naming both consumers that read it - the close-attempt cap and the review-round ceiling. The paired control: an unexplained absence is indistinguishable from an oversight, and the obvious repair is to add the key back - which is the thing a recorded decision forbids. The delivered test checks only that the string `max_rounds` appears, so delivering this criterion strengthens that test until each single-change AC3 mutant in the Test Plan fails it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_config.py::ReviewKeysAreDeclaredTests::test_a_deliberately_absent_key_says_so
  - **Verified:** yes (2026-09-15)

## Impact

A gate refuses, names the setting that caused it, and the setting is undocumented. That is the worst shape a refusal can take: the user is given a lead that goes nowhere, and the cheapest way out is to stop using the gate. It lands hardest on a consuming project, which has neither this repository's history nor its decision log.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `.claude/skills/sdlc-studio/templates/config-defaults.yaml`, delete the `blocking_priority` declaration from the review block | Given every `review.*` key the shipped scripts read, when the defaults file is checked against them, then each key is declared there with its default. Derived from the code rather than from a list, so the next key added is caught rather than exempted by an inventory nobody updated |
| AC2 | in `.claude/skills/sdlc-studio/templates/config-defaults.yaml`, strip the DATE wording from the `test_plan_after` comment | Given `review.test_plan_after` and `review.two_role_after`, when their documentation is read, then it states that the first takes a DATE compared against `Created` and the second takes an ID cutoff - the shared suffix is exactly what makes the wrong guess natural, and one of the two raises on a date while the other silently accepts an id-shaped string |
| AC3 | in `.claude/skills/sdlc-studio/templates/config-defaults.yaml`, delete the note recording why `max_rounds` is absent | Given `review.max_rounds`, which is deliberately absent, when the defaults file is read, then its absence is stated with the reason, on both sides: no uncommented line declares `max_rounds:` as a live key, and the comment that mentions it gives the reason by naming both consumers that read it - the close-attempt cap and the review-round ceiling. The paired control: an unexplained absence is indistinguishable from an oversight, and the obvious repair is to add the key back - which is the thing a recorded decision forbids. The delivered test checks only that the string `max_rounds` appears, so delivering this criterion strengthens that test until each single-change AC3 mutant in the Test Plan fails it |
| AC3 | in .claude/skills/sdlc-studio/templates/config-defaults.yaml, keep the note word for word and insert a live `max_rounds: 3` line under `review:` beneath it - the obvious wrong repair, which the delivered string-presence test survives | Given `review.max_rounds`, which is deliberately absent, when the defaults file is read, then its absence is stated with the reason, on both sides: no uncommented line declares `max_rounds:` as a live key, and the comment that mentions it gives the reason by naming both consumers that read it - the close-attempt cap and the review-round ceiling. The paired control: an unexplained absence is indistinguishable from an oversight, and the obvious repair is to add the key back - which is the thing a recorded decision forbids. The delivered test checks only that the string `max_rounds` appears, so delivering this criterion strengthens that test until each single-change AC3 mutant in the Test Plan fails it |
| AC3 | in .claude/skills/sdlc-studio/templates/config-defaults.yaml, cut the five-line comment to the single line `# review.max_rounds is deliberately absent.`, dropping the two consumers and every word of why, while adding no key | Given `review.max_rounds`, which is deliberately absent, when the defaults file is read, then its absence is stated with the reason, on both sides: no uncommented line declares `max_rounds:` as a live key, and the comment that mentions it gives the reason by naming both consumers that read it - the close-attempt cap and the review-round ceiling. The paired control: an unexplained absence is indistinguishable from an oversight, and the obvious repair is to add the key back - which is the thing a recorded decision forbids. The delivered test checks only that the string `max_rounds` appears, so delivering this criterion strengthens that test until each single-change AC3 mutant in the Test Plan fails it |

## Coverage Rulings

| File | Line | Hash | Reason | Author | Date |
| --- | --- | --- | --- | --- | --- |
| .claude/skills/sdlc-studio/scripts/tests/test_config.py | 296 | 6a3f9d266da42440 | test helper branch reached only when a live max_rounds key exists, which is the AC3b mutant state the test is written to refuse; on the shipped defaults it never runs | sdlc-studio | 2026-09-15 |
| .claude/skills/sdlc-studio/scripts/tests/test_config.py | 334 | 6a3f9d266da42440 | PyYAML-absent skip; every interpreter that runs this suite has PyYAML, which config.py itself requires | sdlc-studio | 2026-09-15 |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-11 | Claude Opus 5 | Filed |
| 2026-09-15 | backlog sweep 2026-09-15 | Backlog sweep 2026-09-15: delivered under its own id by 57704161 (config-defaults.yaml declares every non-exempt review.* key; ReviewKeysAreDeclaredTests pass; a deletion mutant is killed). Fixed is refused for want of a Verification depth, a coverage base ref and an independent test-plan approval - owed, not waived. |
| 2026-09-15 | sprint plan repair 2026-09-15 | Plan review r1 repair. The two-edit AC3 row is split into two single-change rows, each surviving the delivered string-presence test: (a) the note kept word for word with a live max_rounds: 3 inserted under review:, (b) the note cut to one bare line naming neither consumer nor any reason, no key added. AC3 now states both sides - no uncommented max_rounds: line, and the comment names both consumers (the close-attempt cap and the review-round ceiling) - and that delivering it strengthens the existing test_a_deliberately_absent_key_says_so until both die. The production file already satisfies AC3, so probe reads it delivered by design; the defect is the test's. Pre-existing AC1 (f-string reads, key regex not bound to the review block) and AC2 (overlapping DATE/ID windows) test weaknesses left for separate filing: not regressions, and outside the settled scope of this repair. |
| 2026-09-25 | Claude Opus 5.5 | AC2 retired by US0911 (D0259 pattern): `review.test_plan_after` is deleted, so no DATE cutoff is left to tell apart from `review.two_role_after` |
