# BG0192: cross-epic-ac is a bare keyword match and false-positives on common English words

> **Status:** Fixed
> **Severity:** Low
> **Points:** 3
> **Verification depth:** functional (unit tests over strength, per-owner counting, story-frequency suppression and the audit wiring; five mutants executed and killed)
> **Affects:** .claude/skills/sdlc-studio/scripts/ac_scope.py
> **Created:** 2026-07-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`ac_scope.check` flags a story whenever an AC contains a word appearing in another epic's title, with no sense of context. US0219 AC1 ('a rolling local history' of test-suite wall-times) was blocked as belonging to EP0076 'Rolling multi-sprint policy' - unrelated meanings of 'rolling'. This blocks a tranche audit on a wording coincidence, and the only remedies are to reword innocent prose or rescope an AC that was already correctly scoped.

## Steps to Reproduce

1. Ensure an epic exists whose title contains a common word (EP0076 'Rolling multi-sprint policy'). 2. Write a story AC in a different epic using that word in an unrelated sense ('a rolling local history'). 3. Run 'audit.py check --ids <story>'. 4. Observe NOT READY cross-epic-ac naming the unrelated owner epic.

## Proposed Fix

Require more than a single common-word hit before flagging: match on multi-word phrases or distinctive/rare terms, weight by title specificity, ignore a stop-word list, or downgrade a single-keyword hit to an informational note rather than a readiness blocker.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-18 | sdlc-studio | Filed |
| 2026-07-18 | sdlc-studio | Fixed: `ac_scope` findings now carry `strength` (distinct keywords from the same owner epic) and `advisory`; `audit` blocks readiness only on a multi-keyword hit and reports a single-keyword one as a note. Adds document-frequency suppression by story count. Every one of the 11 findings this check produced against the repo was an ordinary English word - the check documents itself as advisory and is now wired as such |
