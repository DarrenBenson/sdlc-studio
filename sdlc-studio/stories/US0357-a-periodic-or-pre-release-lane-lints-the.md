# US0357: a periodic or pre-release lane lints the entire markdown corpus

> **Status:** Draft
> **Delivers:** CR0348
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0123
> **Points:** 3
> **Affects:** tools/lint_corpus.py, tools/tests/test_lint_corpus.py, .github/workflows/lint.yml, package.json

## User Story

**As a** maintainer of this repository
**I want** one lane that lints every tracked markdown file under the strict rule set, on a schedule and before a release
**So that** a latent markdown defect is attributed to the change that introduced it rather than to the next unrelated change that happens to touch the file

## Acceptance Criteria

### AC1: The corpus lane enumerates every tracked markdown file, dot-directories included

- **Given** a repository whose shipped payload lives under `.claude/`, which the `**/*.md` glob the per-commit lanes use cannot see
- **When** the corpus lane enumerates its inputs from the tracked file list rather than from a shell glob
- **Then** every tracked `.md` file is in the enumeration, payload files included, and untracked or ignored trees such as `node_modules/` and `.claude/worktrees/` are not
- **Verify:** pytest tools/tests/test_lint_corpus.py::CorpusEnumerationTests::test_tracked_payload_markdown_is_enumerated_despite_the_dot_directory

### AC2: The strict rule set is applied to the whole corpus, including the payload

- **Given** a payload file carrying a defect that the payload markdownlint config relaxes away (an unescaped table pipe reading as extra columns is the observed case)
- **When** the corpus lane runs
- **Then** the defect is reported with its file, rule id and line, so a class of failure the per-commit lanes never check is visible somewhere
- **Verify:** pytest tools/tests/test_lint_corpus.py::StrictRuleSetTests::test_a_rule_the_payload_config_relaxes_is_still_reported_by_the_corpus_lane

### AC3: The lane runs periodically and before a release, and adds nothing to the per-commit gate

- **Given** the pre-commit gate already runs about 197 seconds against a 120 second budget
- **When** the corpus lane is wired up
- **Then** it is invoked from a scheduled or pre-release workflow job and from an npm script, and no `run` lane for it exists in `.githooks/pre-commit`
- **Verify:** pytest tools/tests/test_lint_corpus.py::LaneWiringTests::test_the_corpus_lane_is_scheduled_and_absent_from_the_precommit_hook

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed: real ACs + Affects authored |
| 2026-07-24 | sdlc-studio | Built TDD: `tools/lint_corpus.py` + `npm run lint:corpus` + scheduled `corpus` CI job; 3 ACs green, mutation-proven |
