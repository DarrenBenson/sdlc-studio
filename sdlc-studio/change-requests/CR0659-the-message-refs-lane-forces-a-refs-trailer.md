# CR-0659: The message-refs lane forces a Refs trailer for any id a subject names, though a trailer attributes the commit's files to that unit

> **Status:** Complete
> **Decomposed-into:** EP0297
> **Priority:** Low
> **Type:** Feature
> **Date:** 2026-11-02
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-02T09:14:45Z

## Summary

2026-11-02, US1110's repair. The commit-msg hook's message-refs lane refused the subject 'docs(US1110): the notes name BG0989's summary refusal, ...' twice until every id it names carried a `Refs:` trailer. But a `Refs:` trailer tells the engagement floor that the named unit owns the commit's files. BG0989 owns none of them; the subject only mentioned it. The builder had to drop BG0989 from the subject, which made the subject say less than it meant.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Recommendation

Option 2: it keeps the rule that every id a subject names is accounted for, without a false attribution.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | claude | Raised |
