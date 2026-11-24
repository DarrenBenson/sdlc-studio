# BG1735: BG1574 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 5
> **Affects:** .githooks/commit-msg, .claude/skills/sdlc-studio/scripts/changelog.py, .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/reference-scripts-surface.md, tools/tests/test_commit_msg_hook.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py, changelog.d/BG1574.md, .claude/skills/sdlc-studio/scripts/tests/test_changelog.py
> **Created:** 2026-11-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-24T03:10:36Z

## Summary

BG1574 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] The refusal prints a schema 3 id as its normalised key, a spelling no artefact carries: `required` builds each fault as `f"{i}: the commit stages code but not ..."` from the `norm_id` key (changelog.py:252, added in 780bd2935), so the shipped hook in a fixture answers `fix(BG-01JQK3F8, BG9002): two` (BG-01JQK3F8's Affects owning the staged `src/v3.py`) with "BG01JQK3F8: the commit stages code but not changelog.d/BG-01JQK3F8.md", while `sdlc_md.display_id` gives `BG-01JQK3F8` for the same workspace and the `norm_id` docstring calls its result "A KEY, never a display" to be printed through `display_id`. A sequential id is unaffected (BG9001 prints as BG9001). I missed this in round one. No open bug covers it.; RULINGS: Round-one findings, judged by execution through the shipped hook in fixture repositories with a positive control beside each refusal. 1 "A shared commit is refused for a `Refs:` id that owns no staged code" CLOSED: `docs(BG9001, BG9002): record verdicts` staging BG9001's record, BG9002's `src/b.py` and `changelog.d/BG9002.md` passes, and without BG9002's fragment it is refused naming BG9002 alone. With three ids, a code owner with no fragment is still refused while a record-only US9003 is not asked. Replayed over main's last 120 first-parent commits, a253272a8 and e2a109be6 now pass. 2 "The new `changelog.py required` call is unguarded" CLOSED: the repaired hook over the base commit's scripts passes `chore: tidy` and passes `fix(BG9001): x` with code and no fragment, and with no changelog.py it passes too, while over the round-one scripts and over the repaired scripts the same unit commit is refused. The header now says the rule alone is skipped. 3 "The id grammar's story and request branches are unpinned" CLOSED: my round-one survivors, re-applied (US and CR dropped, the legacy dash dropped, `Refs:` read case-sensitively, `sorted(refs)`, the relaxed exemption dash), are all killed by ChangelogFragmentRequiredTests, and US9003 and CR9004 commits are refused without their fragments and pass with them. 4 "A fragment named in the dashed spelling of a sequential id is refused" CLOSED: `changelog.d/BG-9001.md` answers both `fix(BG-9001)` and `fix(BG9001)`, another unit's dashed fragment does not, and the refusal still names `changelog.d/BG9001.md`. Repair mutants, each applied once, its test seen red and the file restored: dropping the id-in-name branch, dropping the Affects branch, dropping the shared-commit filter, both `fragment_names` order and spelling changes, the hook with no verb guard, a guard that never matches, and an absent artefact owning everything are all KILLED. No new false refusal found: a v3 shared commit, an unreadable record of a `Refs:` id (no crash), a directory and a glob in Affects, and a staged file name with a space and a non-ASCII letter all behave as documented, and the slowest replayed commit took 4.5 s in `required`. The three replay refusals that remain (44b6d7d4f BG1707, af8f56aa3 BG1717, 7aa9e935b BG1714) are correct under AC3: each is a "did not converge in review" bug whose Affects owns the staged code, none has ever had a fragment, and its parent's fragment does not name it, so the commit owed a fragment or a `Changelog: none - <reason>` saying the parent's entry covers it. That trailer will recur on every non-convergence repair commit, a cost worth a follow-up but not a defect here. Observed, not a finding: a shared commit whose named ids own only records now passes while staging code of an unnamed unit (CR9004's `src/d.py`), as the fragment and the lane text say, and a single-id subject staging another unit's file is still refused. Claim inventory for the repair (commit body, fragment, the `_code_owners` and `fragment_names` docstrings, the hook header and comment) TRUE as exercised above. verify\_ac dry-run reports 4 of 4. At b6581ad8d, `tools/tests/test_commit_msg_hook.py`, `tools/tests/test_lean_commit_lanes.py`, `tools/tests/test_test_census.py` and FragmentInAffectsAtRefineTests give 115 passed and 1 failed. The failure, ImportabilityTests, is a collection error in `tools/tests/test_lint_corpus.py` (markdownlint not found in a fresh worktree with no node\_modules) and fails the same way at the base e09d378e, so it is environmental and not this unit's.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1574 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1574 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] The refusal prints a schema 3 id as its normalised key, a spelling no artefact carries: `required` builds each fault as `f"{i}: the commit stages code but not ..."` from the `norm_id` key (changelog.py:252, added in 780bd2935), so the shipped hook in a fixture answers `fix(BG-01JQK3F8, BG9002): two` (BG-01JQK3F8's Affects owning the staged `src/v3.py`) with "BG01JQK3F8: the commit stages code but not changelog.d/BG-01JQK3F8.md", while `sdlc_md.display_id` gives `BG-01JQK3F8` for the same workspace and the `norm_id` docstring calls its result "A KEY, never a display" to be printed through `display_id`. A sequential id is unaffected (BG9001 prints as BG9001). I missed this in round one. No open bug covers it.
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG1574 AC1 still passes: Given a clone with a `changelog.d/` directory, when a commit whose subject names one unit (`fix(BG9001): ...`) stages a skill script and no `changelog.d/BG9001.md` is staged or tracked, then commit-msg refuses, naming BG9001 and the missing path `changelog.d/BG9001.md`. Fails on: HEAD, which passes it (measured: exit 0, `message rules green - 1 lane(s) passed`).
  - **Verify:** pytest tools/tests/test_commit_msg_hook.py::ChangelogFragmentRequiredTests::test_a_unit_commit_with_a_code_change_and_no_fragment_is_refused
  - **Verified:** yes (2026-11-24)
- [ ] **AC3** BG1574 AC2 still passes: Given the same clone, when the commit stages its fragment, or the fragment is already tracked at HEAD from an earlier commit of the unit, or the commit stages only files under `sdlc-studio/`, or its subject names no unit, then commit-msg passes. Fails on: a fix that refuses a repair-round commit whose fragment landed earlier, or a paperwork commit such as a run close.
  - **Verify:** pytest tools/tests/test_commit_msg_hook.py::ChangelogFragmentRequiredTests::test_a_staged_or_tracked_fragment_or_a_paperwork_commit_passes
  - **Verified:** yes (2026-11-24)
- [ ] **AC4** BG1574 AC3 still passes: Given a shared commit whose subject names BG9001 and BG9002, each owning a staged code file (`Refs:`), with only `changelog.d/BG9001.md` staged, then commit-msg refuses naming BG9002 alone; a `Mentions:` id needs no fragment; a `Changelog: none - <reason>` trailer passes the commit and a bare `Changelog: none` refuses. Fails on: HEAD, which passes all of them; a fix that reads only the subject's first id or accepts an exemption with no reason.
  - **Verify:** pytest tools/tests/test_commit_msg_hook.py::ChangelogFragmentRequiredTests::test_each_owning_id_needs_its_fragment_and_an_exemption_needs_a_reason
  - **Verified:** yes (2026-11-24)
- [ ] **AC5** BG1574 AC4 still passes: Given a project with a `changelog.d/` directory, when `refine.py apply` mints stories, then each story's Affects ends with `changelog.d/<its id>.md`; in a project with no `changelog.d/` no fragment path is added. Fails on: HEAD's refine, which mints Affects with no fragment.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::FragmentInAffectsAtRefineTests
  - **Verified:** yes (2026-11-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-24 | sdlc-studio | Filed |
