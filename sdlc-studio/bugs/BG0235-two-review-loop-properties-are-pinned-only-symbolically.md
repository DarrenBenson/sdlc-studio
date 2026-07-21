# BG0235: two review-loop properties are pinned only symbolically or in aggregate, so a single-class break ships green

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The independent close review of US0261-US0265 (RUN-01KY03GS) APPROVED but surfaced two test-completeness gaps, both confirmed by mutation. First, `DEFAULT_REVIEW_CEILING` = 3 in critic.py is asserted only through the symbol - `test_ceiling_resolves_from_config` compares `review_ceiling` to `DEFAULT_REVIEW_CEILING`, and `test_the_offer_carries` checks str(`DEFAULT_REVIEW_CEILING)` is present - so mutating the literal to 99 leaves the whole critic suite green. US0261 says "default 3" but nothing pins the 3. Second, the _PRIMING classes in `neutrality_violations` are pinned only in aggregate: the one primed-text test trips the verdict-word, severity-label, round-number and asserted-conclusion regexes at once and asserts only truthiness, so neutering any single class regex leaves the suite green and a future break of one class would ship silently. Neither is a live defect - the config-override and guard behaviour ARE pinned, and no primed brief escapes today because brief construction independently omits priming - but both are properties a reader would assume are covered and are not.

## Steps to Reproduce

critic.py: change `DEFAULT_REVIEW_CEILING` = 3 to 99, purge `__pycache__`, run python3 -B -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p `test_critic.py` -> OK (should fail). Separately, replace the MAJOR|MINOR|BLOCKING regex in _PRIMING with a token that matches nothing -> suite still OK (a severity label would no longer be caught as priming, unpinned).

## Proposed Fix

Add a value test for the ceiling default (assert `DEFAULT_REVIEW_CEILING` == 3 directly, or drive `review_ceiling` with no config and assert the numeric refusal boundary). Split `test_neutrality_check_is_mechanical` into one case per priming class - a verdict word alone, a severity label alone, a round number alone, an asserted conclusion alone - each asserting that class is flagged, so a single-class regression fails one test. Mutation-check the new tests.

## Resolution

Test-only; `critic.py` is unchanged. Both gaps reproduced by mutation before the fix, both
mutants surviving the whole 89-test critic suite.

The ceiling is now pinned twice, by value and by behaviour.
`test_the_shipped_ceiling_default_is_three` asserts `DEFAULT_REVIEW_CEILING == 3` and that
`review_ceiling` on a config-less repo returns 3.
`test_the_default_ceiling_refuses_the_fourth_round_not_the_third` drives
`review_round_guard` with no explicit ceiling and pins the boundary from both sides: two
recorded rounds return, three raise. Setting the constant to 99 or to 2 kills both tests; the
pre-existing `review_ceiling == DEFAULT_REVIEW_CEILING` comparison killed neither.

`test_neutrality_check_is_mechanical` is split into one test per priming class - verdict word,
severity label, round number, asserted conclusion - each driven by text carrying only that
class and asserting the EXACT violation list rather than truthiness, so a class that starts
over-firing fails too. The clean-text case keeps its own test. Every listed alternative is
exercised (both verdict words, all three severity labels, all four conclusion phrasings).

Mutation-proven (bytecode purged, `python3 -B`): neutering any one `_PRIMING` regexp to a
non-matching token kills exactly one test, and a different test for each of the four - the
single-class isolation this bug asked for.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Filed |
| 2026-07-21 | sdlc-studio | Fixed - ceiling pinned by value and by boundary, priming split one test per class, all mutation-proven |
