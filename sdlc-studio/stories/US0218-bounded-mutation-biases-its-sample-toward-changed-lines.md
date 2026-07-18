# US0218: bounded mutation biases its sample toward changed lines

> **Status:** Review
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py
> **Epic:** EP0072
> **Points:** 5

## User Story

**As an** engineer mutation-checking a change on a large file
**I want** the cost ceiling spent on the lines I actually changed
**So that** the kill rate is evidence about my diff, not about untouched helpers

## Acceptance Criteria

### AC1: Mutants on changed lines are spent before untouched code

- **Given** a changed-lines set and more enumerable mutants than the ceiling allows
- **When** the budget is applied
- **Then** every selected mutant sits on a changed line until the on-diff pool is exhausted, so a low ceiling on a large file no longer samples whichever lines happen to sort first.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_mutation.DiffBiasedBudgetTests.test_on_diff_mutants_are_chosen_first
- **Verified:** yes (2026-07-18)

### AC2: Once the diff is covered the remaining ceiling spreads broadly

- **Given** a changed-lines set whose on-diff mutants number fewer than the ceiling
- **When** the budget is applied
- **Then** the diff is fully covered and the remainder is spent round-robin over the untouched code, so a small diff does not waste the rest of the budget.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_mutation.DiffBiasedBudgetTests.test_remainder_spreads_over_untouched_code
- **Verified:** yes (2026-07-18)

### AC3: The report states the diff coverage achieved

- **Given** a run whose ceiling cannot reach every mutant on the changed lines
- **When** the report is written
- **Then** the summary carries `diff_mutations`, `diff_applied` and `diff_covered: false`, so a partially-judged diff is legible rather than inferred from the truncation count.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_mutation.DiffBiasedBudgetTests.test_report_states_diff_coverage
- **Verified:** yes (2026-07-18)

### AC4: Without a changed-lines set the existing rotation is unchanged

- **Given** no diff information (an explicit `--files` or `--story` surface)
- **When** the budget is applied
- **Then** selection is the existing deterministic round-robin over (file, fault class) and no diff-coverage keys appear, so the unbiased path is untouched.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_mutation.DiffBiasedBudgetTests.test_no_diff_info_keeps_round_robin
- **Verified:** yes (2026-07-18)

### AC5: The changed-line map is parsed from the diff

- **Given** a repository with a committed baseline and subsequent edits
- **When** `changed_lines` reads `git diff -U0`
- **Then** it returns the touched line numbers per file, counts an untracked file as wholly new, and returns an empty map (rather than failing) when git cannot answer.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_mutation.ChangedLinesTests
- **Verified:** yes (2026-07-18)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-18 | sdlc-studio | Groomed: ACs and executable Verify lines authored |
