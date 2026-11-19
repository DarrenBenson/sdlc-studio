# BG1531: The TRD lists critic brief, gate and review_prep as read-only helpers although each one writes

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** sdlc-studio/trd.md, .claude/skills/sdlc-studio/scripts/tests/test_confinement.py, tools/tests/test_lean_trd_refresh.py, changelog.d/BG1531.md
> **Evidence:** audit AUDIT-2026-11-17, project profile, trd lens, survived 3 of 3 refute votes; observed at sdlc-studio/trd.md §3 Markdown / Python split (lines 155-161); §5 rule 5 (283-284); §2 Pattern Used (85-86); §9 Threat Model row 1 (763); against §3 gate tier (180-187), §6 rows at 556, 601 and 602, and scripts/critic.py:217-228 and 3471-3484
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:23:10Z

## Summary

Section 3 of `sdlc-studio/trd.md` (lines 155 to 161) and rule 5 of section 5 (lines 283 and 284) list `critic brief`, `gate` and `review_prep` among the read-only helpers that never mutate the workspace, and section 2 still calls the whole script layer read-only. The same document says elsewhere that `critic.py brief` writes `briefs.jsonl` and issues the verdict file, that the gate writes state under `.local/`, and that `review_prep.py` writes `review-state.json`. In code, `critic.py brief` also creates a verdict folder (`issue_verdict_file`, lines 217 to 228) and appends a brief note (`note_brief`, lines 3471 to 3484). The threat model row in section 9 (line 763) rests its mitigation on this read-only list and cites a write-confinement snapshot suite, but the read-only tests in `test_confinement.py` cover only status, conformance, integrity, reconcile detect and readiness. Two descriptions of one write surface disagree, and the tested list is shorter than the claimed one.

## Steps to Reproduce

1. Read `sdlc-studio/trd.md` lines 155 to 157 and 283 to 284: `critic brief`, `gate` and `review_prep` are named as read-only helpers that never mutate the workspace.
2. Read lines 180, 601 and 602 of the same file: the gate writes untracked state under `.local/`, `critic.py brief` writes `briefs.jsonl`, and `review_prep.py` writes `review-state.json`.
3. Read `issue_verdict_file` and `note_brief` in `.claude/skills/sdlc-studio/scripts/critic.py`: both create directories and write files during a brief.
4. Read the read-only tests in `.claude/skills/sdlc-studio/scripts/tests/test_confinement.py` (lines 62 to 74): none runs `critic.py brief`, `gate.py` or `review_prep.py`.
5. Expected: one statement of which helpers are read-only, matching the code and held by a test. Actual: the list contradicts sections 3 and 6 of the same document and the code, and the cited suite does not cover the three helpers.

## Proposed Fix

In `sdlc-studio/trd.md`, remove `critic brief`, `gate` and `review_prep` from the read-only lists in sections 3 and 5, describe each as a helper that writes only its named state (naming the files and whether each is tracked), reword the section 2 pattern line so the script layer is not called read-only, and make the section 9 mitigation cite the lists as corrected. In `test_confinement.py`, add a test for each of the three helpers that snapshots a fixture workspace and asserts the run writes only the paths the TRD names for it, and a test that every helper the TRD still calls read-only has a read-only assertion in the suite.

## Acceptance Criteria

- [ ] **AC1** Given sections 2, 3, 5 and 9 of `sdlc-studio/trd.md`, when they are read, then `critic brief`, `gate` and `review_prep` are in no read-only list, each is described as writing only its named state with the files and whether each is tracked, section 2 does not call the script layer read-only, and the section 9 mitigation cites the corrected lists. Fails on: any of the three still listed as never mutating the workspace.
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdReadOnlyHelperTests::test_the_writing_helpers_are_not_listed_as_read_only
- [ ] **AC2** Given a snapshot of a fixture workspace, when `critic.py brief`, `gate.py` and `review_prep.py` are each run through their CLI, then each changes only the paths the TRD names for it (the verdict folder, `briefs.jsonl` and the brief note; state under `.local/`; `review-state.json`). Fails on: a write outside the named paths, or a named path the helper does not write.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_confinement.py::WritingHelperConfinementTests::test_each_writing_helper_writes_only_its_named_state
- [ ] **AC3** Given the helpers the TRD still calls read-only, when the list is compared with the read-only assertions in `test_confinement.py`, then every one has an assertion there. Fails on: a helper claimed read-only that no confinement test runs.
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdReadOnlyHelperTests::test_every_helper_called_read_only_has_a_confinement_assertion

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
