# BG1715: BG1229 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_record_shapes.py, changelog.d/BG1229.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-11-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-22T23:09:37Z

## Summary

BG1229 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] The markdownlint half of AC1 part three cannot fail. `test_the_row_passes_markdownlint` (test\_critic\_record\_shapes.py:270-282) lints the row for the class's ISSUES fixture (line 248), and that row passes markdownlint with the asterisk left bare. With the `_BARE_ASTERISK` substitution removed from `_escape_outside_spans` and the main checkout's markdownlint found, the test passes (mutant SURVIVED, run alone). The raw row also lints clean when written through `critic.py record` in a fixture (lint exit 0, no MD037). An asterisk sitting directly between two code spans has no space inside its markers, so MD037 never fires there. The class docstring's "two of them in one row pair into emphasis (MD037) unless each is escaped" (line 244) is therefore FALSE for this fixture, and only the escape test kills the mutant. The shape the bug reports does fail raw: a row naming two globs, each a code span followed by a bare asterisk and a space, is refused with MD037 when bare (lint exit 1) and passes once escaped (exit 0), both written through `critic.py record` in a fixture. Add that shape to the lint test, keeping AC1's own example, and correct the docstring [LC-018]; RULINGS: Round-1 blocking 1, the asterisk test skipping before assertions that need no linter, is CLOSED. The escape and read-back checks now sit in test\_each\_asterisk\_between\_spans\_is\_escaped\_and\_reads\_back\_bare, which needs no linter. With `_markdownlint` forced to find nothing, that test passes at HEAD and kills both the bare-asterisk mutant and the read-back mutant (`\*` not undone), and the brief's replay of "the asterisk left bare" now reports killed. The lint test's skip message names the places it looked, matching `_markdownlint` (PATH, then node\_modules/.bin in this checkout and in the main worktree). Round-1 blocking 2, the dry run's reviewer, author and brief cells untested, is CLOSED. Cutting the `_clean` loop in `_dry_run_verdict` (critic.py:5847) down to the issues cell fails 3 subtests, and dropping the author cell alone fails 1. The three subtests still kill the cut with their message assertion removed. Through the CLI, the real record and the dry run both refuse an odd backtick in each of the three cells (exit 2), and a clean control passes both. Round-1 blocking 3, the fragment's FALSE: wording, is CLOSED. changelog.d/BG1229.md now says a TRUE or UNVERIFIABLE claim so ruled is recorded and a FALSE one is refused with its evidence named. test\_a\_ruling\_with\_its\_evidence\_records\_as\_the\_ruling and test\_a\_false\_ruling\_with\_evidence\_is\_still\_refused\_naming\_it show this through `critic.py self-check record`: TRUE 2 and UNVERIFIABLE 1 are recorded, and the FALSE claim is refused with "nothing is cached" in the refusal and no row written. Claim inventory of the repair: the commit message's BG1229 paragraph is TRUE, except that "markdownlint runs in a test of its own" needs the ISSUES finding's qualification: the test runs, but it cannot fail on the escape. The dry-run test's docstring no longer lists the review cap, and that is TRUE because the cap has a test of its own. Verify line green (`verify_ac.py run --id BG1229 --dry-run`: ac=1 pass=1). The author's recorded mutants replay killed, and test\_critic\_record\_shapes.py passes in my detached worktree (10 passed). Not judged here: the `critic.py` and `test_critic.py` hunks of 30eb84a5 and 286a57c6 that belong to the other units of those commits

## Steps to Reproduce

1. Read the round 2 REJECT of BG1229 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1229 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] The markdownlint half of AC1 part three cannot fail. `test_the_row_passes_markdownlint` (test\_critic\_record\_shapes.py:270-282) lints the row for the class's ISSUES fixture (line 248), and that row passes markdownlint with the asterisk left bare. With the `_BARE_ASTERISK` substitution removed from `_escape_outside_spans` and the main checkout's markdownlint found, the test passes (mutant SURVIVED, run alone). The raw row also lints clean when written through `critic.py record` in a fixture (lint exit 0, no MD037). An asterisk sitting directly between two code spans has no space inside its markers, so MD037 never fires there. The class docstring's "two of them in one row pair into emphasis (MD037) unless each is escaped" (line 244) is therefore FALSE for this fixture, and only the escape test kills the mutant. The shape the bug reports does fail raw: a row naming two globs, each a code span followed by a bare asterisk and a space, is refused with MD037 when bare (lint exit 1) and passes once escaped (exit 0), both written through `critic.py record` in a fixture. Add that shape to the lint test, keeping AC1's own example, and correct the docstring [LC-018]
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG1229 AC1 still passes: A ruling 'TRUE: evidence' records as TRUE with its evidence kept; record --dry-run validates a verdict and writes nothing; a verdict naming `a_`*`_b` writes a ledger row markdownlint passes.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_record_shapes.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-22 | sdlc-studio | Filed |
