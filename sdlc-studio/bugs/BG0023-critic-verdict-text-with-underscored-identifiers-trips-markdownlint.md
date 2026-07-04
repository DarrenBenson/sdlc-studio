# BG0023: critic verdict text with underscored identifiers trips markdownlint MD037

> **Status:** Closed
> **Created:** 2026-06-21
> **Created-by:** sdlc-studio new
> **Severity:** Low

## Summary

Recording a critic verdict whose issues text contains underscored identifiers (e.g. `_read`,
`_index_row`) wrote them verbatim into `sdlc-studio/reviews/critic-verdicts.md`, where two such
tokens pair across words into a markdown emphasis span with spaces, tripping markdownlint MD037.
Caught by the lint gate twice (CR0057, CR0063), each needing a manual fix.

## Steps to Reproduce

`critic.py record --issues "fixed _read and _index_row"` -> the appended row trips MD037 on the
next `npm run lint`.

## Proposed Fix

Escape `_` in `critic._clean` (the free-text-cell sanitiser that already handles `|` and newlines)
so underscores cannot form emphasis. Fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | sdlc | Created via `new` (deterministic) |
