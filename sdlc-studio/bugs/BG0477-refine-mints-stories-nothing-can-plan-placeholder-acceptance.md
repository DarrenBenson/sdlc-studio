# BG0477: refine mints stories nothing can plan: placeholder acceptance criteria, unfilled user-story fields, and a persona that is no seat

> **Status:** Open
> **Severity:** High
> **Points:** 5
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

- [ ] **AC1: a story minted from a request that HAS criteria carries seeded criteria, not a placeholder.**
  - **Given** a request whose own acceptance criteria are authored, and a breakdown naming three
    stories
  - **When** `refine.py apply` runs without `--no-seed-acs`
  - **Then** each minted story carries at least one seeded criterion naming a real surface rather
    than the ungroomed placeholder, because `--no-seed-acs` already implies seeding is the
    default and twenty stories in one run arrived with none
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::SeededCriteriaTests::test_a_request_with_criteria_seeds_its_stories

- [ ] **AC2: a seeded story is not thereby claimed groomed.**
  - **Given** the stories minted by AC1
  - **When** `sprint.py breakdown` runs over them
  - **Then** they are still reported as owing grooming, because a seeded draft is a better
    starting point and not an authored criterion - the census must not read a seed as authored
    or this fix would hide the very debt it exists to price
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::SeededCriteriaTests::test_a_seed_is_not_counted_as_authored

- [ ] **AC3: the user-story fields are filled, and `Persona:` names a resolvable seat or is absent.**
  - **Given** a minted story
  - **When** it is read back
  - **Then** no `{{role}}`, `{{capability}}` or `{{benefit}}` placeholder remains, and any
    `Persona:` value resolves through `persona_resolve.py` - naming somebody who is in no seat
    file is worse than naming nobody
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::SeededCriteriaTests::test_no_placeholder_fields_and_a_resolvable_persona

- [ ] **AC4: the grooming still owed is REPORTED at refine time, in units the planner uses.**
  - **Given** a completed `refine apply`
  - **When** it prints its result
  - **Then** it names how many minted stories still owe authored criteria, so the unpriced work
    is visible when the batch is planned rather than discovered as a full-batch refusal - this is
    the honest-price half of the fix and it holds whether or not seeding is enabled
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::SeededCriteriaTests::test_refine_reports_the_grooming_it_leaves_owed

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Filed |
