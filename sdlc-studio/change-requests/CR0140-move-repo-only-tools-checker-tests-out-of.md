# CR-0140: move repo-only tools/ checker tests out of the shipped skill payload (payload hygiene)

> **Status:** Complete
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Improvement
> **Affects:** tools/tests/ (new), .claude/skills/sdlc-studio/scripts/tests/, package.json, .githooks/pre-commit, AGENTS.md
> **Depends on:** -

## Summary

The repo-only CI checkers (`tools/check_neutrality.py`, `check_budgets`, `check_links`,
`check_versions`, `validate_skill`) are correctly **not** shipped in the skill payload, and the
portable `gate.py` does not run them - so a consuming project never has, for example, its own project
names blocked by the domain-neutrality guard. Good. But their **unit tests** sat inside the shipped
payload at `.claude/skills/sdlc-studio/scripts/tests/`, reaching the checker via
`Path(__file__).resolve().parents[5] / "tools" / ...` (up to the repo root).

That is a payload-boundary leak: those five test files shipped into every consumer install (verified
on a fresh `~` install), tested tools that do **not** ship, and would error if a consumer ran the
skill's test suite (there is no `tools/` at `parents[5]` of an installed copy). The shipped payload
should test only what ships.

Fix: relocate the five `tools/` checker tests to a repo-level `tools/tests/`, repoint their paths,
and rewire the runners so both suites run in dev and CI while the payload tests only shipped scripts.
`test_version_check.py` stays in `scripts/tests/` - it tests `scripts/version_check.py`, which is
genuine payload.

## Acceptance Criteria

- [x] `test_check_neutrality/budgets/links/versions.py` + `test_validate_skill.py` moved from
      `.claude/skills/sdlc-studio/scripts/tests/` to `tools/tests/` (via `git mv`, history kept)
- [x] their paths repointed: checker at `parents[1]`, repo root at `parents[2]`, skill dir at
      `parents[2]/.claude/skills/sdlc-studio` - both suites pass from the new layout
- [x] the total test count is preserved (995 = 958 skill + 37 tools) - no test lost
- [x] runners run both suites: `package.json` (`test` -> `test:skill` + `test:tools`), the
      pre-commit hook (two `run` steps), and CI (`npm test`); the coverage run stays scoped to the
      shipped scripts
- [x] the shipped payload no longer contains a test that references a non-shipped `tools/` path
- [x] AGENTS.md documents the two suites; `CHANGELOG.md` `[Unreleased]` ([[LL0004]])

## Out of Scope

- Moving `check_*` scripts themselves - they already live in `tools/` (repo-only); only their tests
  were misplaced.
- Adding a coverage floor for `tools/` (it was never gated; unchanged here).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | claude | Created via `new` (deterministic) |
| 2026-07-04 | claude | Implemented: moved 5 tests to tools/tests, repointed paths, rewired runners; 995 preserved; Complete |
