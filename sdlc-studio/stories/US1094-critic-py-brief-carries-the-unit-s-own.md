# US1094: critic.py brief carries the unit's own capped diff and the command that runs its Verify lines, and each review tier states the sections it carries and its tool-call budget

> **Status:** Ready
> **Delivers:** CR0651
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_review_brief_diff.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/help/review.md, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/templates/config-defaults.yaml, changelog.d/US1094.md
> **Epic:** EP0292
> **Points:** 3
> **Depends on:** US1089
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, paying for one independent review of every unit
**I want** the reviewer handed the unit's diff against the run's base, bounded to its Affects and capped with the remainder named, and the one command that runs its Verify lines, with the light tier materially lighter and each tier stating a tool-call budget
**So that** a review spends its turns judging the change rather than finding it, and a low-risk unit costs a light review

## Acceptance Criteria

- **AC1:** Given a fixture repository with an open run naming the unit and its base commit, and commits since that base changing two Affects files and one undeclared file, when `critic.py brief --unit <id> --seat qa` runs, then stdout carries a unit-diff section equal to the output of `git diff <base> HEAD -- <Affects>`, the undeclared file's hunks are absent, and the fingerprint printed on stderr is the one `critic.brief_fingerprint(critic.brief(...))` gives
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_brief_diff.py::ReviewBriefDiffTests::test_the_brief_carries_the_units_own_diff_bounded_to_affects
- **AC2:** Given a diff longer than the tier's cap (`review.brief_diff_lines`, its full and light defaults declared once), then the section holds the diff up to the cap and one remainder line naming each file cut or left out, its omitted line count and the `git diff <base> HEAD -- <file>` that prints it; a diff within the cap carries no remainder line
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_brief_diff.py::ReviewBriefDiffTests::test_a_diff_over_the_cap_names_what_it_left_out
- **AC3:** Given a unit, then the brief carries the one command that runs that unit's Verify lines without writing its story file (`verify_ac.py run --id <id> --dry-run`, with the skill's script path); given no run naming the unit, the brief says no base is recorded, carries no diff section, and still carries the command
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_brief_diff.py::ReviewBriefDiffTests::test_the_brief_names_the_command_that_runs_the_units_verify_lines
- **AC4:** Given one unit briefed at each tier through `critic.py brief --tier full|light`, then the set of section headings in each brief equals `TIER_SECTIONS[tier]` and the practices `missing_practices` finds present equal `TIER_PRACTICES[tier]` (light omits the claim inventory, the files' history and the two mutation practices, and keeps the isolated-checkout and repair practices), the light diff cap is below full's, each brief states its tier's tool-call budget from `TIER_TOOL_BUDGET`, and the light brief is not refused for the practices its tier omits
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_brief_diff.py::ReviewTierTests::test_each_tier_carries_its_declared_sections_practices_and_budget

## Notes

- Serves: Maya Okafor, End goal 3.
- AC1 must fail on: the diff taken with no pathspec (unbounded); the working tree diffed against the base, which shows uncommitted work an isolated reviewer's checkout cannot see; the diff printed on stderr, outside the brief the reviewer reads and the fingerprint covers
- AC2 must fail on: silent truncation; a remainder that gives a count but no command; the cap typed in the renderer rather than read from the declared defaults and the config key
- AC3 must fail on: the command omitted or naming another unit; the command without `--dry-run`, which ticks criteria in the author's story file; a diff taken from a run about other work
- AC4 must fail on: the light tier rendering full's sections; the budget typed in the depth line rather than read from the table; `assert_brief_practices` still demanding all five practices at light, which refuses every light brief
- `critic.py brief` spends about 19 of its 20 s in `reconcile.file_history_section`, uncached; that is filed separately, not fixed here.
- Overlap: id: BG0982; relation: related, stays its own: E3 keeps the Affects bound the operator specified, so an undeclared change is still invisible; BG0982's 'changed but not declared' block would sit beside E3's remainder line; evidence: AC1: 'For a unit whose commits since the run's base change a file its Affects does not declare, `critic.py brief` names that file in a ''changed but not declared'' block'
- Overlap: id: BG0970; relation: related, stays its own: E3 diffs base..HEAD, so uncommitted work stays out of the brief; BG0970 warns about it; evidence: Title: '`critic.py brief` says nothing when the unit's Affects carry uncommitted changes, though it sends the reviewer to an isolated worktree that cannot see them'
- Overlap: id: BG1108; relation: related: E3 reads the base from `run_state.unit_run_base_ref`; BG1108 corrects that base for a carried unit, and E3's diff section then shows the repair rather than an empty diff; evidence: AC1: 'The brief for a carried unit's redelivery names a diff from the commit its capping REJECT judged'
- Overlap: id: US1049; relation: related: same base reader, for a small change no run names (E3 AC3's no-base branch); evidence: AC1: 'the brief prints `git diff <base> -- <Affects>` with that base and the `verify_ac.py revert-check --unit <id>` command'
- Overlap: id: BG0975; relation: related: a lighter light tier raises the cost of a rejoinder wrongly derived as light; worth delivering before or with E3; evidence: Title: 'critic.py brief --rejoinder derives a light tier from the risk band even when the round it answers was taken at an explicit full tier'
- Overlap: id: US1089; relation: seam on `cmd_brief`: both add to the same verb; EP0291 ships first (D0389 (2)); evidence: AC1: 'when `critic.py brief` runs at any tier, then it exits 2 naming `critic.py self-check record`'
- Risk: Measured (US1087, in-process, nothing written): the full brief is 10,579 characters and the light one 10,050 (5% smaller). The brief itself is about 2.6k tokens against a 1.9M review, so the saving comes from the diff and the budget cutting exploration turns, not from a shorter brief.
- Risk: Measured: `brief()` took 19.9 s, of which `reconcile.file_history_section` took 19.0 s (`unit_corpus` 18.4 s; `backlog_triage._affect_key` 9.3 s, `sdlc_md.resolve_affects` 5.9 s). `lane_dispatch` wraps the same call in `sdlc_md.corpus_cache()`; `critic.brief` does not. Dropping the history at light makes light fast; the full tier stays slow, which is worth filing as its own performance bug.
- Risk: Light dropping two practices reverses reference-review.md:457 ('refuses a delivery brief at every tier ... missing any of these practices'). The isolated-checkout practice is kept at light on purpose: it protects the author's tree.
- Risk: The fingerprint now covers the diff, so briefs taken before and after a fix commit differ. `rebrief_notice` compares Affects and criteria only and `record` stores the fingerprint without judging it, so nothing refuses; fixtures that compare fingerprints across commits (tests/test_lean_file_history.py) may need adjusting.
- Risk: The tool-call budget is stated, not enforced. Enforcing it needs E1's subagent reading (counting `tool_use` blocks per reviewer transcript) and is a follow-up.
- Risk: Tight at 3 points: four criteria across the diff, the cap, the command and a tier table. If the tier table grows, split AC4.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | sdlc-studio | Created via `new` (deterministic) |
