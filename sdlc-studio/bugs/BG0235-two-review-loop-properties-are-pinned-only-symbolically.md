# BG0235: two review-loop properties are pinned only symbolically or in aggregate, so a single-class break ships green

> **Status:** Open
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

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Filed |
