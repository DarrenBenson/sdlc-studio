# US1300: `critic.py record` stores the author's and reviewer's model ids on the verdict and derives each family from one shipped table, reporting an unknown id as unknown

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0732
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/lib/model_family.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_cross_family.py, changelog.d/US1300.md
> **Epic:** EP0369
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** `critic.py record` stores the author's and reviewer's model ids on the verdict and derives each family from one shipped table, reporting an unknown id as unknown
**So that** CR0732 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Both model ids are on the verdict row

- **Given** a unit in a throwaway project with an empty verdict ledger
- **When** `critic.py record --unit <id> --verdict APPROVE --author-model claude-opus-5-5 --reviewer-model gpt-5.4` is run
- **Then** the ledger row carries both ids, and the ledger reader returns each with its family (anthropic and openai). Fails on: either id dropped, or only the family kept so the record cannot say which model wrote or judged the diff
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_cross_family.py::RecordModelsTests::test_the_row_carries_both_model_ids_and_their_families

### AC2: One table gives the family, and an id it does not know reads unknown

- **Given** `lib/model_family.py`'s one table of id patterns per family
- **When** `claude-opus-5-5` (the API's dashed form), `claude-sonnet-5.5` (Copilot's dotted form), an OpenAI id, a Google id and `acme-coder-2` are looked up
- **Then** the first four resolve to anthropic, anthropic, openai and google, and `acme-coder-2` resolves to `unknown`. Fails on: an unmatched id guessed into a family (the author's, or the first in the table), or the dotted Copilot form missing its family
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_cross_family.py::FamilyTableTests::test_known_ids_resolve_and_an_unlisted_id_reads_unknown

### AC3: Rows written before the change, and records without models, read unchanged

- **Given** a ledger holding rows in each earlier shape (seven, eight and nine cells), and a new record made with neither model flag
- **When** the ledger is read and the unit's rounds and independence are computed
- **Then** the earlier rows read with both models `unknown`, the round count and independence verdicts are what they were before the change, and the record without flags is written with `-` in both model cells. Fails on: a cell shift that reads an old row's issues or Source as a model, or a record refused for want of a model while `review.cross_family` is off
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_cross_family.py::LegacyRowsTests::test_rows_written_before_the_model_cells_read_unchanged

## Notes

- The ledger has three earlier row shapes (`_COLS`, `_DELIVERY_COLS`, the nine-cell Source row). Append the model cells after Source so every earlier shape stays a prefix; whether that is two cells or one `author/reviewer` cell is the builder's choice.
- Family patterns are prefixes (`claude-` is anthropic). The table lives in one module so `sprint_report.py` (US1302) reads the same answer.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-17 | Claude Opus 5.5 (grooming) | Groomed: authored criteria with Verify lines, Affects corrected to the skill's test folder and this unit's fragment, notes |
