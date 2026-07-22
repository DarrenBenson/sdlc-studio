# BG0258: The docs-checker's escape enumeration has been wrong at three, four, five, six and seven, because each repair enumerates instead of deriving

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_docs_single_writer.py
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Five consecutive review rounds each found an escape the previous enumeration had denied. Round 3 found item 4 (an unrelated negation within `NEG_REACH` launders an assertion, which the comment explicitly said could not happen). Round 4 found item 5 (a sentence with every topic word but no enumerated ASSERTING word is never judged). Round 5 found item 6 (normalise strips asterisk emphasis but not underscore, so `_proves_` escapes where `*proves*` is caught). Round 6 found item 7: an axis fires only when EVERY topic group matches, and AC3's object group is a closed list, so any synonym for the staged tree escapes selection entirely - and items 1 and 5 positively DENY that case, so a maintainer reading the list concluded those sentences were judged. Each round's author believed they had understood the previous failure and wrote a corrected count; the count was wrong again every time. Round 7 found item 8, and it is the one item 2 explicitly EXCLUDED: a polarity cue outside the closed NEG_CUES vocabulary, so 'A review without a declared window is perfectly fine' is a direct denial that reads as an assertion. Round 9 then found the same class on the OVER-fire side, where a count had just been introduced while correcting one: the scan reads only backwards from the asserting word, so a postposed cue is invisible and a natural paraphrase of the guarded rule is flagged as its own opposite. The pattern is the same one CR0394 names for guard messages: an enumeration of a rule that lives elsewhere in code is a restatement, and a restatement is only correct until the rule moves. Here the rule is emergent from three enumerated lists interacting, which is precisely the shape a human cannot enumerate reliably.

## Steps to Reproduce

1. Read THE BOUND in `test_docs_single_writer.py`, which enumerates the escapes. 2. Construct a sentence that contradicts a guarded property while matching only SOME of an axis's topic groups, for example 'A green gate proves the working copy is uncontaminated'. 3. Append it to the shipped reference-sprint.md in memory and call `check_all.` Observed: it escapes cleanly, and no item in the enumeration covers it while items 1 and 5 deny it. Repeat historically: the same procedure found a new escape against the three-, four-, five-, six- and seven-item versions.

## Proposed Fix

Stop enumerating. Derive the disclosure from the mechanism: report, for a candidate sentence, WHICH axis selected it and WHY it was or was not judged, so a maintainer asking 'would this be caught' gets an answer from the code rather than from a list a human maintains. Failing that, generate the escape corpus rather than hand-writing it - the escapes found so far were each found by an adversary constructing a sentence, which is a search a fuzzer can do continuously. Whatever is chosen, the enumeration must stop being presented as a boundary; it has been a lower bound five times running.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Filed |
