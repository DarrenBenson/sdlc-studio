# US1057: Sprint plan names each blocked persona card with its remedy and each card owed a review, and the release cut names the owed reviews

> **Status:** Draft
> **Delivers:** CR0631
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_review.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/release_cut.py, .claude/skills/sdlc-studio/best-practices/persona.md, .claude/skills/sdlc-studio/reference-persona.md, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/help/persona.md, .claude/skills/sdlc-studio/reference-scripts-domain.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_persona_review_owed.py, changelog.d/US1057.md
> **Epic:** EP0287
> **Points:** 5
> **Depends on:** US1055
> **Persona:** Maya Okafor

## User Story

**As a** Jonah Reyes, upgrading the skill and cutting releases on a schedule
**I want** `sprint plan` to name each persona card the standard now refuses with its remedy, and `persona_review.py owed`, the plan and the release cut to name each card changed since its review or not reviewed since the latest release tag
**So that** a refused card is found where I plan rather than mid-run, and the review runs on every change and once per release because my usual commands say it is owed

## Acceptance Criteria

- **AC1:** Given a project seat card naming a persona the cast does not declare, when `sprint.py plan` runs, then it prints one `persona card blocked:` line naming the card, the rule, the line and the remedy, with the plan's exit code and batch unchanged.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_review_owed.py::PersonaReviewOwedTests::test_the_plan_names_each_blocked_card_with_its_remedy
- **AC2:** Given three cards in a repository with no tags, one with a PASS at its current bytes, one edited since its PASS and one never reviewed, when `persona_review.py owed` runs, then it names the second as changed since its review of that date and the third as never reviewed, and not the first.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_review_owed.py::PersonaReviewOwedTests::test_changed_and_unreviewed_cards_are_owed
- **AC3:** Given a card whose PASS is dated the day before the newest release tag's commit, and an unchanged card whose PASS is dated the tag commit's own day, when `persona_review.py owed` runs, then it names the first as not reviewed since that tag and not the second.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_review_owed.py::PersonaReviewOwedTests::test_a_card_not_reviewed_since_the_latest_tag_is_owed_by_day
- **AC4:** Given an owed card, when `sprint.py plan` and `release_cut.py changelog-cut --version 9.9.9` run, then each prints one `persona review owed:` line naming it, and the plan's exit code and batch and the cut's CHANGELOG.md are the same as with no card owed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_review_owed.py::PersonaReviewOwedTests::test_the_plan_and_the_release_cut_name_owed_reviews

## Notes

- Release: 6.2 (D0355 breakdown G13, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the plan silent about a card every review in the run will refuse, so the stop lands mid-run in `critic.py brief`, which has no --skip-personas
- AC2 must fail on: change judged by mtime or git history instead of the recorded body hash, so a reviewed marker reads as a change and a reverted edit as none
- AC3 must fail on: the newest tag chosen by name order rather than commit date, a same-day review compared against the commit's timestamp, or a repository with no tags erroring
- AC4 must fail on: either command refuses on an owed review (D7 blocks a failing card, not an owed review), or only one of them prints the list
- Serves: Jonah Reyes #4 (upgrade safely) and #3.
- Checked at HEAD: nothing compares a card with any review record; `release_cut.py` (changelog-cut, record-green, tag-check) and `sprint plan` say nothing about personas.
- D0364: sprint plan names each blocked card with its remedy. Owed reviews are reported, never refused (panel Q7: no yield measured; revisit once reviews are measured).
- Days: a review dated on or after the tag commit's date counts as since the tag.
- Adds persona-review-owed (reported, under Freshness) to `persona_review.py check` and the standard page. reference-review.md's Persona Review pass names owed reviews from this command (one line replaced; the page sits near its budget).
- Re-sized 3 to 5 for the blocked-card line (panel).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G13 after the refine panel's review |
