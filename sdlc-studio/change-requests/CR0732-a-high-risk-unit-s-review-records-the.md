# CR-0732: A high-risk unit's review records the model family of its author and its reviewer, and a project can require the two to differ

> **Status:** In Progress
> **Decomposed-into:** EP0369
> **Priority:** Medium
> **Type:** Feature
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, tools/tests/test_critic_cross_family.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** competitor review 2026-11-17: published accounts of a commercial autonomous-delivery platform (Blitzy), chiefly its CEO and CTO interview on The Cognitive Revolution (January 2026) and the Quesma audit of its SWE-Bench Pro run; compared against this skill by grep
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T21:37:55Z

## Summary

The doctrine says to prefer cross-model review for high-stakes units, because a second instance of the same model shares the first one's blind spots. Nothing records or checks it: `critic.py record` takes free-text --author and --reviewer strings and no model, so a verdict cannot say which model wrote the diff or which judged it, and no report can count how often the advice was followed. A commercial platform in the same space makes this a hard rule (a reviewer must come from a different model family than the agent it reviews) and reports that it measurably improves results. Record the two model ids on every verdict, derive each one's family, and add a `review.cross_family` setting (off, warn, block) that applies to units whose risk class is high.

## Impact

Any project running autonomous sprints on components it has classed high risk. Today the independence of a review is one fresh context of the same model, and the record cannot show otherwise.

## Acceptance Criteria

- [ ] `critic.py record` stores the author's and the reviewer's model id on the verdict row, and refuses a record for a high-risk unit that names neither when `review.cross_family` is warn or block
- [ ] A family is derived from a model id by one shipped table, and an id the table does not know is reported as unknown, never guessed
- [ ] With `review.cross_family: block`, a same-family verdict on a high-risk unit does not count as that unit's independent review; with warn it counts and the report says so; with off nothing changes
- [ ] The sprint report states how many high-risk units were reviewed by a different family, out of how many

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
