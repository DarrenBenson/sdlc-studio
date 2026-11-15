# BG1177: README's 6.2.0 line and the notes' theme heading say a reviewer judges only self-checked work, though the shipped default only reports a missing self-check

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** README.md, docs/release-notes-v6.2.0.md, tools/tests/test_lean_release_notes_v62.py, tools/tests/test_self_check_claim_wording.py, changelog.d/BG1177.md
> **Created:** 2026-11-02
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-02T21:04:53Z

## Summary

Found by US1111's review (2026-11-02). README.md:474 calls 6.2.0 the release where 'a reviewer judges only work its author has self-checked', and docs/release-notes-v6.2.0.md:12 heads its first theme the same way. But `review.author_self_check` ships as `report` (templates/config-defaults.yaml:87), and under `report` `critic.py brief` still prints the brief with a notice (critic.py:3113-3114). Only `block` refuses it. The notes' body and their opening line qualify it. The README line does not.

## Steps to Reproduce

1. Read README.md:474.
2. On a fresh project, run `critic.py brief --unit <id> --seat qa` with no self-check recorded: the brief prints.

## Proposed Fix

Word the README line and the theme heading as the notes' opening line does: a review brief can now require the author's own check first.

## Acceptance Criteria

- [ ] **AC1** Given docs/release-notes-v6.2.0.md, when its first theme bullet and its theme table row are read, then both say a review brief can require the author's own check first, and neither says a reviewer judges only self-checked work.
  - **Verify:** pytest tools/tests/test_self_check_claim_wording.py::SelfCheckClaimWordingTests::test_the_62_notes_say_a_brief_can_require_the_self_check
  - **Verified:** yes (2026-11-15)
- [ ] **AC2** Given README.md, when every line naming the author's self-check is read, then none says a reviewer judges only self-checked work.
  - **Verify:** pytest tools/tests/test_self_check_claim_wording.py::SelfCheckClaimWordingTests::test_the_readme_claims_no_enforced_self_check
  - **Verified:** yes (2026-11-15)
- [ ] **AC3** Given the renamed theme, when the 6.2 notes' lead test runs, then it passes with THEMES keyed on the new heading and the same four units.
  - **Verify:** pytest tools/tests/test_lean_release_notes_v62.py::ReleaseNotesTests::test_the_notes_lead_with_what_changed_for_you
  - **Verified:** yes (2026-11-15)

## Impact

A reader of the front page believes self-checks are enforced by default.

## Notes

- AC1 must fail on: docs/release-notes-v6.2.0.md:12 or :176 as they stand
- AC2 must fail on: README.md:480 as it stands
- AC3 must fail on: THEMES (test_lean_release_notes_v62.py:47-48) left on the old heading
- Still true at HEAD: README.md:480, docs/release-notes-v6.2.0.md:12 and :176; config-defaults.yaml:87 ships `review.author_self_check: report`, under which `critic.py brief` prints the brief.
- The filed Verify ran the whole module; replaced with named tests. The README check is phrased so it survives CR0702's README rewrite, which may drop the line.
- Shares README.md with CR0702's README story: same lane, BG1177 first.
- End goal 1 (the front door claims only what the shipped default enforces).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | claude | Filed |
| 2026-11-15 | Claude Opus 5.5 (run fourteen grooming, D0479) | Groomed for run fourteen: Affects, criteria with Verify lines, notes |
