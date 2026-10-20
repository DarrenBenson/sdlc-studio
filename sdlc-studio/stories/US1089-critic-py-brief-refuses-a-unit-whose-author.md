# US1089: critic.py brief refuses a unit whose author has recorded no self-check for its current diff

> **Status:** Ready
> **Delivers:** CR0650
> **Created:** 2026-10-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_refusal.py, .claude/skills/sdlc-studio/reference-review.md, sdlc-studio/.config.yaml, AGENTS.md, changelog.d/US1089.md
> **Epic:** EP0291
> **Points:** 3
> **Depends on:** US1088
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, whose reviewer should confirm her work rather than discover it
**I want** `critic.py brief` to refuse a unit whose author has recorded no self-check of its current diff
**So that** no reviewer is briefed on work its author has not checked first, including a repair before its re-review

## Acceptance Criteria

- **AC1:** Given `review.author_self_check: block` and a unit with no self-check record, when `critic.py brief` runs, then it exits 2 naming `critic.py self-check record`, prints no brief on stdout and notes no brief fingerprint
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_refusal.py::SelfCheckRefusalTests::test_no_record_is_refused
- **AC2:** Given `block` and a record whose Affects digest no longer matches the unit's Affects content, when the brief runs, first-round or `--rejoinder`, then it is refused the same way and names the record as stale
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_refusal.py::SelfCheckRefusalTests::test_a_stale_record_is_refused
- **AC3:** Given `block` and a record whose digest matches, when the brief runs, then it prints the brief and its fingerprint as it does without the setting
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_refusal.py::SelfCheckRefusalTests::test_a_current_record_admits_the_brief
- **AC4:** Given `report`, the shipped default, and no current record, when the brief runs, then it prints the brief and stderr names the missing or stale record; given `off`, then stderr says nothing of it; and this repository's `sdlc-studio/.config.yaml` sets `block`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_refusal.py::SelfCheckRefusalTests::test_the_setting_decides_refuse_report_or_silence

## Notes

- Serves: Maya Okafor, End goal 3.
- Delivers CR0650's refusal half of part (3) (D0382). A consuming project upgrading gets `report`, so its brief is not refused on the first run after an upgrade; this repository blocks.
- AC1 must fail on: the refusal printed after the brief, or after `note_brief` has recorded a fingerprint.
- AC2 must fail on: the `--rejoinder` path skipping the check, so a repair is re-reviewed on a self-check of the code it replaced.
- AC3 must fail on: a matching record still refused (the positive control).
- AC4 must fail on: the shipped default set to `block`, or `off` still printing.
- AGENTS.md's paragraph on exercising every claim before review calls itself ungated; it names this gate instead.
- Depends on US1088, whose record and digest this reads.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-20 | sdlc-studio | Created via `new` (deterministic) |
