# US1089: critic.py brief refuses a unit whose author has recorded no self-check for its current diff

> **Status:** Ready
> **Delivers:** CR0650
> **Created:** 2026-10-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_refusal.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/templates/config-defaults.yaml, sdlc-studio/.config.yaml, AGENTS.md, tools/tests/test_author_self_check_repo.py, changelog.d/US1089.md
> **Epic:** EP0291
> **Points:** 3
> **Depends on:** US1088
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, whose reviewer should confirm her work rather than discover it
**I want** `critic.py brief` to refuse a unit whose author has recorded no self-check of its current diff
**So that** no reviewer is briefed on work its author has not checked first, including a repair before its re-review

## Acceptance Criteria

- **AC1:** Given `review.author_self_check: block` and a unit with no self-check record, when `critic.py brief` runs at any tier, then it exits 2 naming `critic.py self-check record`, prints no brief on stdout, notes no brief fingerprint, and still prints US1087's author self-check section on stderr so the author is told what to record
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_refusal.py::SelfCheckRefusalTests::test_no_record_is_refused_with_the_steps
- **AC2:** Given `block` and a record whose Affects digest no longer matches the unit's Affects content, when the brief runs, first-round or `--rejoinder`, at any tier, then it is refused the same way and names the record as stale
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_refusal.py::SelfCheckRefusalTests::test_a_stale_record_is_refused
- **AC3:** Given `block` and a record whose digest matches, when the brief runs, then it prints the brief and its fingerprint as it does without the setting
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_refusal.py::SelfCheckRefusalTests::test_a_current_record_admits_the_brief
- **AC4:** Given a project with `review.author_self_check` unset, when the brief runs with no current record, then it prints the brief and stderr names the missing or stale record; given `off`, then stderr says nothing of it; and `templates/config-defaults.yaml` and `reference-config.md` give the key with default `report`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_refusal.py::SelfCheckRefusalTests::test_the_setting_decides_refuse_report_or_silence
- **AC5:** Given this repository, when its `sdlc-studio/.config.yaml` and AGENTS.md are read, then the config sets `review.author_self_check: block`, and the AGENTS.md paragraph led by `Exercise every claim through the shipped entry point before asking for review.` names `critic.py self-check record` and `review.author_self_check` and names neither `CR0520` nor `lane-check`
  - **Verify:** pytest tools/tests/test_author_self_check_repo.py::AuthorSelfCheckRepoTests::test_this_repository_blocks_and_says_so

## Notes

- Serves: Maya Okafor, End goal 3.
- Delivers CR0650's refusal half of part (3) (D0382, D0383). A consuming project upgrading gets `report`, so its brief is not refused on its first review after an upgrade; this repository blocks.
- AC1 must fail on: the refusal printed after the brief or after `note_brief`; the steps withheld on a refusal.
- AC2 must fail on: the `--rejoinder` path or the light tier skipping the check.
- AC3 must fail on: a matching record still refused (the positive control).
- AC4 must fail on: the shipped default set to `block`, which only a test leaving the key unset can see; `off` still printing.
- AC5 must fail on: AGENTS.md keeping 'Ungated until CR0520 ships `verify_ac lane-check`' beside the new names; this repository's config left at the default.
- Goal review amendment round, 2026-10-21 (engineering): AC4's repository clause and AC5 read this repository's own files, so they live in `tools/tests`, which never installs, not in the shipped `scripts/tests`.
- Limits, stated: the digest covers whole files, so a sibling unit's edit to a shared Affects file stales a record, which is a change to what is reviewed. `critic.py record` stores a fingerprint no brief here noted, by design for a brief taken in another clone, so a hand-written brief is not stopped here; AGENTS.md's rule against hand-written briefs covers it. Depends on US1088.
- Run order (Goal review amendment round, 2026-10-21, both seats): BG1000, US1087 and US1088 are built and committed before US1089, and no unit in the run is briefed for review until US1089 is committed and a self-check is recorded for that unit, so every brief critic.py issues in this run passes the gate.
- Goal review, 2026-10-21 (engineering, product and qa seats) added the steps on refusal, the tiers, the unset-key test, the config documents and AC5.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-20 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-21 | Claude Opus 5.5 | Regroomed on the run-three goal review's two rounds (engineering, product and qa seats; D0384) |
| 2026-10-22 | sdlc | Correction (US1087 QA review, 2026-10-22): e58c7bcd's D0386 paragraph names host-proven tree 0be4e30d, the tree of its worktree original cb49765b; the cherry-pick on main has tree 25bf3cdc, proven only within the push tip 69951ff0 (gate green) |
