# CR-0113: ac_scope / cross-epic-ac false-positives on shared domain vocabulary (cry-wolf in the audit)

> **Status:** Complete
> **Priority:** High
> **Type:** Improvement
> **Date:** 2026-06-25
> **Created-by:** sdlc-studio file

## Summary

ac_scope flags a story whose AC contains a keyword distinctive to ANOTHER epic's title. But it only filters a small generic stopword set (_STOP) - not the project's domain nouns. So 'list' (owned by EP0002 List Management) and 'item' fire on every story that mentions a list/item, including done stories and the EP0005 web-client stories that legitimately display lists/items. A field agent planning EP0005 saw all 7 stories + US0002-US0007 flagged cross-epic-ac and correctly dismissed it as 'a noisy keyword heuristic'. Wiring it into the tranche audit made the noise prominent - a low-precision advisory that fires on everything trains operators to ignore it. Refine the heuristic so it suppresses shared domain vocabulary.

## Acceptance Criteria

- [x] ac_scope suppresses a 'distinctive' keyword when it has high document frequency across stories (it appears in stories of many epics / above a threshold) - such a word is shared domain vocabulary, not epic-specific leakage
- [x] the EP0005 web-client stories (and done stories) no longer trip cross-epic-ac on 'list'/'item'; a genuine reference to another epic's distinctive concept still flags
- [x] unit test: a domain noun used across >=N stories is not flagged; a concentrated cross-epic keyword is; CHANGELOG entry
- [x] if precision cannot be made high enough, reconsider whether cross-epic-ac belongs in the default audit vs an opt-in lint (do not cry-wolf)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-25 | audit | Raised |
