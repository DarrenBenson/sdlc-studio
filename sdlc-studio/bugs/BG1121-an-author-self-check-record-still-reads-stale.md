# BG1121: An author self-check record still reads stale in landing orders the per-file own-change view cannot see through: work recorded before its own commit, a cherry-pick, or another unit's hunk in a file the author also changed

> **Status:** Open
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_self_check_hunk_binding.py, .claude/skills/sdlc-studio/scripts/tests/test_self_check_survives_a_later_unit.py, .claude/skills/sdlc-studio/help/review.md, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-config.md, sdlc-studio/reviews/author-self-checks.md, .claude/skills/sdlc-studio/scripts/tests/test_confinement.py, changelog.d/BG1121.md
> **Evidence:** BG1117 QA review round 1, qa-seat-BG1117-r1, at 57a2bb7a: blocking finding 1's cases and the pre-existing US1089 case. Reproduced at cecc9dfe through `critic.py brief` in a throwaway repository, 2026-11-24.
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-22T13:35:46Z

## Summary

BG1117's QA review (round 1, 2026-10-22). BG1117 sets aside other units' later commits per file, stopping at the unit's own newest commit (`_own_change_digest` in critic.py), which handles a record taken after the unit's own commit has landed. Two landing orders still read stale at HEAD. First, the author records uncommitted work in a shared file, another unit commits only its own hunk to that file, then the author's commit lands: the author's commit is the file's newest, so the view reads its content, which holds the other unit's hunk the record never saw. Second, the unit's commit is cherry-picked onto another branch: the record's commit is not an ancestor of HEAD, so `_own_change_digest` returns None and the gate falls back to the content as it stands, which any later commit to the file moves. BG1117's own motivating case is the first: US1089's recorded digest 9bd14739 is e58c7bcd's content without US1090's AGENTS.md hunk, and it still reads stale with the commit a74e8352. Fixing these needs binding to the unit's own change (its hunks or the patch id of its diff), not per-file content.

The order where another unit's hunk lands after the author's own commit is already handled: the view sets that commit aside and reads the author's.

## Steps to Reproduce

In a throwaway repository with `review.author_self_check: block`, where US0101 and US0102 both declare `src/shared.py`:

1. US0101 edits `src/shared.py` and records its self-check uncommitted; US0102 commits only its own new function to that file; US0101 commits its recorded edit on top. `critic.py brief --unit US0101 --seat qa` exits 2: "is stale".
2. US0101 commits on a side branch and records there; main takes a commit of US0102's, cherry-picks US0101's commit, then US0102 adds its own function to `src/shared.py`. The brief on main exits 2: "is stale".

## Proposed Fix

Bind the record to the unit's own change: the diff of its uncommitted and committed work against the record's base, restricted to Affects, compared hunk by hunk with the unit's own diff now (its commits against their parents plus any uncommitted edit); or record the patch id of that diff and match it after a cherry-pick. Then correct the pages that describe the binding.

## Acceptance Criteria

- [ ] **AC1** Given US0101's self-check recorded over its uncommitted edit to `src/shared.py`, then US0102's commit of only its own hunk to that file, then US0101's commit of the recorded edit, when US0101 is briefed under `review.author_self_check: block`, then the brief is admitted. Fails on: the per-file view reads US0101's newest commit, which holds US0102's hunk, so the brief exits 2 as stale.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_self_check_hunk_binding.py::HunkBindingTests::test_a_record_before_the_units_commit_survives_a_sibling_landing_first
- [ ] **AC2** Given US0101's self-check recorded at its commit on a side branch, and that commit cherry-picked onto main, where US0102 then commits its own hunk to `src/shared.py`, when US0101 is briefed on main under `block`, then the brief is admitted. Fails on: the record's commit is not an ancestor of HEAD, so the gate falls back to the content as it stands and exits 2 as stale.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_self_check_hunk_binding.py::HunkBindingTests::test_a_cherry_picked_commit_keeps_its_record
- [ ] **AC3** Given either order above followed by one more edit of US0101's own to `src/shared.py` (uncommitted, or committed under US0101's id), or a side-branch record whose commit never reached main, when US0101 is briefed under `block`, then it is refused as stale. Fails on: a binding that checks only that the recorded hunks are present admits work the author never checked (this guard holds today and must still hold after the fix).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_self_check_hunk_binding.py::HunkBindingTests::test_an_unrecorded_hunk_of_the_units_own_still_stales_the_record
- [ ] **AC4** Given the fix, when a reader reads help/review.md, reference-review.md's author self-check section, reference-config.md's `review.author_self_check` row and the self-check log header (`_SELF_CHECK_HEADER` and `sdlc-studio/reviews/author-self-checks.md`), then each describes the binding to the unit's own change and none says uncommitted recorded work is staled by another unit's commit landing first. Fails on: help/review.md:48-49 says a record of uncommitted work can still read as stale, reference-review.md:494-495 says it is staled by another unit's commit landing first, and reference-config.md:238 and the header describe the per-file view.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_self_check_hunk_binding.py::HunkBindingTests::test_the_pages_and_the_log_header_describe_the_hunk_binding

## Impact

Authors re-record unchanged evidence in these orders, the churn BG1117 set out to remove.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | Claude Opus 5.5 | Filed |
| 2026-10-22 | sdlc | BG1117 round-2 QA review: help/review.md:48-49, the critic.py comment at 2690-2691 and the self-check log header (critic.py `_SELF_CHECK_HEADER` and author-self-checks.md) still say a record of committed work survives, which a cherry-pick after another unit's commit contradicts; the fix corrects them, and Affects gains the two doc files (critic.py is already declared) |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: reproduced both orders at cecc9dfe through `critic.py brief`; the order where another unit's hunk lands after the author's commit is already handled; criteria made executable with a guard against admitting an unrecorded hunk and a pages criterion; Affects gains reference-review.md and reference-config.md and drops test_critic.py; Points stay 3 |
| 2026-11-24 | orchestrator | Affects gains tests/test_confinement.py: the fix's merge sides are written to a TemporaryDirectory for `git merge-file`, and the shared-write sweep needs its allowlist entry (the CR builder's full-suite run) |
