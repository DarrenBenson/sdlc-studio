# BG0477: refine mints stories nothing can plan: placeholder acceptance criteria, unfilled user-story fields, and a persona that is no seat

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Verification depth:** functional
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py, .claude/skills/sdlc-studio/templates/core/story.md
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** 2026-08-01T08:00:52Z

## Summary

`refine apply` creates an epic and its stories and wires the links, which is the point. What it hands back cannot be planned: every story carries the ungroomed AC placeholder, the `{{role}}` / `{{capability}}` / `{{benefit}}` fields of the user story are unfilled, and each carries `Persona: Maya Okafor`, who is not in `personas/seats/`. `sprint plan` then refuses the batch as ungroomed, correctly.

Measured this run: refining four CRs produced 20 stories, all 20 ungroomed. Grooming them - authoring 3 to 5 criteria with executable Verify lines each - was the largest single piece of work in the sprint's planning phase and was unpriced, because the points were set on the delivery each story describes. The parent CRs carried detailed acceptance criteria that were not seeded, and `--no-seed-acs` implies seeding is the default.

The lesson is already recorded (skeleton stories: grooming is unestimated work). What is missing is either the seeding or an honest price.

## Steps to Reproduce

1. Write a breakdown file for a CR that carries acceptance criteria.
2. refine.py apply --request CRxxxx --breakdown <file> -> stories created.
3. grep the new stories: each has the ungroomed AC placeholder and {{role}} unfilled.
4. sprint.py breakdown --worklist <the new ids> -> N units, N ungroomed.

## Proposed Fix

Seed each story's criteria from the parent request's, as `--no-seed-acs` implies is the default, even if only as a draft an author then sharpens - a draft criterion naming the right surface is worth more than a placeholder. Fill the user-story fields from the story title, and either resolve a real seat for `Persona:` or omit the field rather than naming somebody who does not exist. If seeding is genuinely out of scope, `refine` should report the grooming it is leaving owed, so the cost is visible at plan time.

## Acceptance Criteria

> **Re-grounded at the plan-time goal review.** The filed summary claimed the parent request's
> criteria "were not seeded". They ARE seeded - onto the EPIC, verbatim, and deliberately:
> commit `7ef88707` removed story-level seeding for a multi-story breakdown because a breakdown
> cannot know which criterion belongs to which story, and replaced the defending test with two
> asserting the opposite. Seeding them back is that defect returning, so it is not asked for.
> The `Persona:` claim was also wrong - the value is the declared Primary resolved by
> `artifact._resolve_persona`, working as designed. What survives is the two defects that
> reproduce, and the unit is re-priced from 5 to 3 accordingly.

- [ ] **AC1: a minted story carries no unfilled template field.**
  - **Given** a breakdown minting three stories from a request
  - **When** `refine.py apply` runs and the stories are read back
  - **Then** no `{{role}}`, `{{capability}}` or `{{benefit}}` placeholder remains in the User
    Story block, because a field the template left for an author to fill is indistinguishable
    from one the author forgot
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::MintedStoryFieldsTests::test_no_template_placeholder_survives_minting

- [ ] **AC2: `refine` reports the grooming it leaves owed, in the planner's own units.**
  - **Given** a completed `refine apply` that minted N stories, all ungroomed by construction
  - **When** it prints its result
  - **Then** it names how many of them still owe authored criteria, so the unpriced work is
    visible when the batch is planned rather than met as a full-batch refusal later - twenty
    stories arrived this way in one run and grooming them was the largest single piece of that
    sprint's planning
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::MintedStoryFieldsTests::test_refine_reports_the_grooming_it_leaves_owed

- [ ] **AC3: the count it reports is the census's answer, not a second one.**
  - **Given** the same minted set
  - **When** the reported count is compared with `sprint.py breakdown` over those ids
  - **Then** they agree, because a creator quoting its own arithmetic is how the planner and the
    creator came to disagree in the first place
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::MintedStoryFieldsTests::test_the_reported_count_matches_the_breakdown_census

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Filed |
