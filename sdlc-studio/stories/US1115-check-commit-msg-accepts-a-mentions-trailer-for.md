# US1115: check-commit-msg accepts a Mentions: trailer for an id the subject only mentions, and the engagement floor attributes no files to it

> **Status:** Ready
> **Delivers:** CR0659
> **Created:** 2026-11-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/engagement_floor.py, .claude/skills/sdlc-studio/reference-scripts-verify.md, .claude/skills/sdlc-studio/help/gate.md, .claude/skills/sdlc-studio/scripts/tests/test_mentions_trailer.py, changelog.d/US1115.md
> **Epic:** EP0297
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** solo founder-engineer committing work that names another unit (Maya)
**I want** to account for an id my commit subject only mentions with a `Mentions:` trailer
**So that** the subject can say what it means without telling the engagement floor that the mentioned unit owns the commit's files

## Acceptance Criteria

- **AC1:** Given a subject naming US1110 and BG0989 with `Refs: US1110` and `Mentions: BG0989`, when `engagement_floor.py check-commit-msg --strict` reads it, then it exits 0, and with the `Mentions:` line removed it exits 1 naming BG0989
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mentions_trailer.py::MentionsTrailerTests::test_a_mentions_trailer_accounts_for_a_mentioned_id
- **AC2:** Given that commit in a fixture repository, when the git leg attributes files through both `_git_touched_by_id` and `_git_touched_source_files`, then US1110 receives the commit's source files and BG0989 receives none
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mentions_trailer.py::MentionsTrailerTests::test_a_mentioned_id_is_attributed_no_files
- **AC3:** Given a subject naming three ids, with `Refs:` for one, `Mentions:` for one and nothing for the third, when `check-commit-msg --strict` runs, then it refuses naming only the third, and the warning offers both `Refs: <id>` (it owns the files) and `Mentions: <id>` (it owns none)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mentions_trailer.py::MentionsTrailerTests::test_an_unaccounted_id_is_named_with_both_remedies

## Notes

- Serves: Maya Okafor, End goal 5. CR0659; D0399. The CR's option 2, chosen at planning: a line-anchored `Mentions:` trailer with the same grammar as `Refs:`, counted by `check_commit_message` as accounting for an id. The git leg reads only `Refs:` and does not change, so no historical commit changes meaning. Option 1 (scope ids as owners) was rejected: it changes the floor's batch test in two functions that must agree (LL0016).
- AC1 must fail on: the Mentions reader returning an empty set, or Mentions lines parsed as Refs.
- AC2 must fail on: `_refs_ids` also reading `Mentions:`. Assert on both functions, since they must agree.
- AC3 must fail on: the warning naming only `Refs:`, as today, or one `Mentions:` line covering every id.
- Risks: an author can mark every id a mention, and the floor then skips the commit, exactly as it skipped a multi-id commit before the Refs rule; that is disclosed, not refused, because a filing commit legitimately owns nothing. An id in both trailers: `Refs:` wins. A prose body line starting `Mentions:` would parse, the same exposure `Refs:` already has.
- Overlaps: US1116 depends on this. help/gate.md:336 and reference-scripts-verify.md:242-244 describe the rule, so update both.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-02 | Claude Opus 5.5 (grooming) | Groomed under D0399 from the run-five planning pass: user story, criteria with Verify lines, mutants and risks |
