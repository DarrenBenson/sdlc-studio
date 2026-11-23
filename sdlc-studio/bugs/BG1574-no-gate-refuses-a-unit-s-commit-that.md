# BG1574: No gate refuses a unit's commit that ships no changelog fragment, so run sixteen landed twelve of fourteen units without one

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .githooks/commit-msg, .claude/skills/sdlc-studio/scripts/changelog.py, .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/reference-scripts-surface.md, tools/tests/test_commit_msg_hook.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py, changelog.d/BG1574.md
> **Evidence:** Run sixteen (RUN-01M7NTY5), 2026-11-18: commits 79519227 (has one), cb445223, b10e40ae, 85b79786 (none).
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T01:05:23Z

## Summary

AGENTS.md says every behaviour or doc change carries its changelog.d/<UNIT-ID>.md fragment (LL0004), but the pre-commit's changelog-shape lane checks only the shape of fragments that are staged. Grooming left the fragment out of most bugs' Affects, builders stage exactly the Affects, and lane land, critic brief and lane accept all passed units with none. Run sixteen landed BG1507, BG1519 to BG1524, US1290 to US1292 and BG1523 with no fragment; two reviewers flagged it as non-blocking, and the fragments were written afterwards in a paperwork commit.

## Steps to Reproduce

1. In a throwaway clone at HEAD, stage a change to `.claude/skills/sdlc-studio/scripts/refine.py`
   and nothing under `changelog.d/`.
2. Write the message `fix(BG1574): change refine with no fragment` and run
   `.githooks/commit-msg <msg-file>`, then `python3 .claude/skills/sdlc-studio/scripts/changelog.py shape --staged`.

Measured at HEAD 3791e5193: commit-msg exits 0 (`message rules green - 1 lane(s) passed`) and
`shape --staged` exits 0 (`0 staged fragment(s) well-formed`). `.githooks/pre-commit --list` and
`.githooks/commit-msg --list` name no lane that asks for a fragment; `changelog-shape` judges only
the fragments a commit stages.

## Proposed Fix

The rule needs the subject, so it belongs in the commit-msg hook (pre-commit runs before the
message exists). Add a `changelog.py` check, run by a new commit-msg lane after `message-refs`,
that reads the unit ids the commit is attributed to (the one id a single-id subject names, or
each `Refs:` id of a shared commit; a `Mentions:` id owns no file and needs none) and, when the
repo keeps a `changelog.d/` directory and the commit stages any path outside `sdlc-studio/` and
`changelog.d/`, refuses unless `changelog.d/<ID>.md` is staged or already tracked at HEAD (a
repair round's fragment landed in its first commit). A `Changelog: none - <reason>` trailer
exempts a commit and must carry a reason. Have `refine apply` add `changelog.d/<story id>.md` to
each minted story's Affects when the project keeps `changelog.d/`. There is no shipped groom
command; the groom is a prompt, so only refine is in scope.

## Acceptance Criteria

- [ ] **AC1** Given a clone with a `changelog.d/` directory, when a commit whose subject names one unit (`fix(BG9001): ...`) stages a skill script and no `changelog.d/BG9001.md` is staged or tracked, then commit-msg refuses, naming BG9001 and the missing path `changelog.d/BG9001.md`. Fails on: HEAD, which passes it (measured: exit 0, `message rules green - 1 lane(s) passed`).
  - **Verify:** pytest tools/tests/test_commit_msg_hook.py::ChangelogFragmentRequiredTests::test_a_unit_commit_with_a_code_change_and_no_fragment_is_refused
- [ ] **AC2** Given the same clone, when the commit stages its fragment, or the fragment is already tracked at HEAD from an earlier commit of the unit, or the commit stages only files under `sdlc-studio/`, or its subject names no unit, then commit-msg passes. Fails on: a fix that refuses a repair-round commit whose fragment landed earlier, or a paperwork commit such as a run close.
  - **Verify:** pytest tools/tests/test_commit_msg_hook.py::ChangelogFragmentRequiredTests::test_a_staged_or_tracked_fragment_or_a_paperwork_commit_passes
- [ ] **AC3** Given a shared commit whose subject names BG9001 and BG9002, each owning a staged code file (`Refs:`), with only `changelog.d/BG9001.md` staged, then commit-msg refuses naming BG9002 alone; a `Mentions:` id needs no fragment; a `Changelog: none - <reason>` trailer passes the commit and a bare `Changelog: none` refuses. Fails on: HEAD, which passes all of them; a fix that reads only the subject's first id or accepts an exemption with no reason.
  - **Verify:** pytest tools/tests/test_commit_msg_hook.py::ChangelogFragmentRequiredTests::test_each_owning_id_needs_its_fragment_and_an_exemption_needs_a_reason
- [ ] **AC4** Given a project with a `changelog.d/` directory, when `refine.py apply` mints stories, then each story's Affects ends with `changelog.d/<its id>.md`; in a project with no `changelog.d/` no fragment path is added. Fails on: HEAD's refine, which mints Affects with no fragment.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::FragmentInAffectsAtRefineTests

## Impact

The release cut's CHANGELOG misses the unit, or the fragment is written later by someone who did not build it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
| 2026-11-23 | Sam Eriksson (qa) | Groomed for run twenty-four: reproduced at HEAD through commit-msg in a clone; the gate moves to commit-msg (pre-commit has no subject), with a `changelog.py` check, a named exemption trailer and refine's default; Affects drops pre-commit, gate.py and the new tools test for the files the fix touches; four executable criteria; 3 to 5 points |
