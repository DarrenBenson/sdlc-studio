# BG0733: a Verified line reading PARTIAL or no is treated exactly like yes, so an honest self-report of a miss is laundered into a green

> **Status:** Fixed
> **Severity:** High
> **Points:** 13
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Verification depth:** functional
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

A criterion's `Verified:` line does not survive contact with the verifier, and the filed summary
understated it. Measured on 2026-09-22 against fixtures driven through the shipped CLI, there are two
distinct failures and neither is "treated like yes".

**A parsed non-`yes` value is OVERWRITTEN.** `- **Verified:** no`, `manual` and `stale` each parse,
and a green selector rewrites all three to `- **Verified:** yes (<today>)`. The honest self-report is
not ignored, it is destroyed, and the file no longer records that anybody doubted the criterion.

**An unparseable value is invisible, and a contradictory line is inserted above it.** `VERIFIED_RE`
demands the value be one of `yes`, `no`, `stale` or `manual`, then an optional parenthetical, then END
OF LINE - so any line carrying a reason misses entirely. The parser then believes the criterion has no
`Verified:` line, inserts a fresh `yes`, and strands the original beneath it: one criterion, two
contradictory verdicts. A census finds 3143 `Verified:` lines, of which 17 sit in that state.

Either way the run reports `pass`, the close counts the unit covered, and the report of record prints
it satisfied. The corpus counts of 18 `manual` and 18 `no` survive only because nothing has re-run
`verify_ac` over those units since; the next run that does will silently green them.

## Steps to Reproduce

1. Build a story with four criteria, each carrying `Verify: shell true` and one of: `Verified: no`,
   `Verified: manual`, `Verified: PARTIAL (date) - reason`, and no `Verified:` line at all.
2. Run `verify_ac.py run --id <id> --root <fixture>`.
3. It reports `ac=4 pass=4 fail=0`. The `no` and `manual` lines have been REWRITTEN to `yes`; the
   PARTIAL line is untouched but now sits below a newly inserted `yes` for the same criterion.
4. `sdlc_md.VERIFIED_RE.match('  - **Verified:** manual - checked by hand')` returns None.
   Reproduced 2026-09-22.

## Proposed Fix

Three parts, because there are three defects.

1. **Widen the parser** so a value may carry a reason after it: the value stays in the vocabulary, the
   parenthetical stays optional, and the remainder is captured as the recorded reason.
2. **Read the value against a POSITIVE SET of `yes` and `manual`.** The census finds 3107 `yes`, 18
   `manual`, 18 `no`; `manual` is this project's own word for hand-verified, so anything-but-`yes`
   would redden 18 satisfied criteria on the run that shipped it.
3. **Never overwrite a recorded verdict with a derived one.** `no` reports NOT satisfied and the line
   stays as written; `manual` reports satisfied and stays `manual`, because the value records HOW the
   criterion was verified; a value outside the vocabulary is reported unreadable rather than buried
   under a second line.

A criterion with no `Verified:` line keeps today's behaviour. BG0463 claim 15 is the same defect in
the `authority` field.

## Acceptance Criteria

- [ ] **AC1: a recorded `no` fails the criterion and is NOT rewritten.**
  - **Given** a criterion whose selector is green and whose `Verified:` line reads `no` with the reason the author recorded
  - **When** `verify_ac.py run` completes
  - **Then** the criterion counts in `fail`, and the line still reads `no` - today it is overwritten with `yes`, destroying the only record that anyone doubted it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::VerifiedFieldIsReadTests::test_a_recorded_no_fails_and_is_not_rewritten
  - **Verified:** yes (2026-09-22)
- [ ] **AC2: `manual` is a positive verdict and keeps its own word.**
  - **Given** a criterion whose selector is green and whose `Verified:` line reads `manual`
  - **When** the run completes
  - **Then** it passes AND the line still reads `manual` - the value records HOW it was verified, so rewriting it to `yes` loses the distinction the author was making
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::VerifiedFieldIsReadTests::test_manual_passes_and_keeps_its_own_word
  - **Verified:** yes (2026-09-22)
- [ ] **AC3: a value carrying a reason parses, and the reason is reported.**
  - **Given** a line reading `manual - byte-identical, confirmed independently by the reviewer`, one of 17 such lines in this corpus
  - **When** the run parses it
  - **Then** the value is `manual` and the reason appears in the run's REPORT under `recorded_reasons` - asserting it on the file proves nothing, because a positive verdict is never rewritten, and the mutant deleting the capture survived a whole module that way
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::VerifiedFieldIsReadTests::test_a_value_with_a_trailing_reason_parses_and_carries_it
  - **Verified:** yes (2026-09-22)
- [ ] **AC4: a value outside the vocabulary is reported unreadable, and no second line is inserted.**
  - **Given** a criterion whose line reads `PARTIAL (2026-09-22) - two of fifteen cases fail`
  - **When** the run completes
  - **Then** it is reported as carrying an unreadable verdict, does NOT pass, and the file still holds exactly one `Verified:` line for that criterion
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::VerifiedFieldIsReadTests::test_an_unreadable_value_is_reported_and_no_second_line_is_inserted
  - **Verified:** yes (2026-09-22)
- [ ] **AC5: a criterion with NO `Verified:` line is unaffected.**
  - **Given** a criterion with a green selector and no `Verified:` line, the shape of 660 of this corpus's 3793 criteria
  - **When** the run completes
  - **Then** it passes and the line is written as today - an absent field is not a denial, and treating it as one would redden the entire backlog at once
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::VerifiedFieldIsReadTests::test_an_absent_verified_line_is_not_a_denial
  - **Verified:** yes (2026-09-22)
- [ ] **AC6: a failing recorded verdict moves no unit's status.**
  - **Given** a Done unit carrying a recorded `no`, of which this corpus holds seven
  - **When** the run reports it failing
  - **Then** the unit's recorded status is untouched - reporting the truth about history is the point, and reopening seven closed units is a separate decision nobody has taken
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::VerifiedFieldIsReadTests::test_a_failing_recorded_verdict_moves_no_status
  - **Verified:** yes (2026-09-22)

- [ ] **AC7: this tool MARKS the downgrades it writes, and only those clear.**
  - **Given** a criterion stamped green whose selector goes red, then goes green again
  - **When** the two runs are driven end to end
  - **Then** the first writes a downgrade carrying the tool's own mark and the second clears it back to `yes` - the author and the tool wrote the identical line, so provenance could not be read from the file at all and had to be recorded
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::VerifiedFieldIsReadTests::test_the_red_fix_green_loop_closes_end_to_end
  - **Verified:** yes (2026-09-22)
- [ ] **AC8: a verdict must be a whole word.**
  - **Given** lines reading `yesterday`, `nope`, `manually by hand` and `stalemate`
  - **When** the pattern is applied
  - **Then** none parses - without the boundary `yesterday` reads as a positive `yes`, and the mutant dropping it survived all 411 tests in the module
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::VerifiedFieldIsReadTests::test_the_value_must_be_a_whole_word
  - **Verified:** yes (2026-09-22)
- [ ] **AC9: `stale` is not a positive verdict.**
  - **Given** a criterion recording `stale` with a reason, over a green selector
  - **When** the run completes
  - **Then** it fails, and `stale` is absent from the positive set - both the changelog and the docstring asserted this and nothing pinned it, so the mutant adding `stale` to the set survived
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::VerifiedFieldIsReadTests::test_stale_is_not_a_positive_verdict
  - **Verified:** yes (2026-09-22)

- [ ] **AC10: an UNMARKED non-positive verdict is protected, and that is the corpus shape.**
  - **Given** criteria recording `no`, `no (2026-07-20)` and `stale`, each bare of any reason, on a unit whose status is Done
  - **When** each is run against a green selector
  - **Then** all three report failing and none is rewritten - every one of this corpus's 18 non-positive lines is bare, so a rule protecting only annotated verdicts protected none of them and destroyed 100% of the real instances
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::VerifiedFieldIsReadTests::test_a_bare_recorded_no_is_protected
  - **Verified:** yes (2026-09-22)
- [ ] **AC11: a flip records the verdict it replaced.**
  - **Given** a marked downgrade cleared by a green selector
  - **When** the run reports its flips
  - **Then** `old_state` names the verdict that was there, not `none` - it is the audit field for exactly this event, and reporting `none` made a cleared verdict indistinguishable from one that never existed
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::VerifiedFieldIsReadTests::test_a_flip_records_what_it_replaced
  - **Verified:** yes (2026-09-22)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `verify_ac.py`, restore the write-through that sets a green criterion's `Verified:` line to `yes` whatever it already recorded - the shipped behaviour | |
| AC2 | in `verify_ac.py`, widen the flip condition from `not recorded` to `recorded != yes`, so a green selector rewrites a recorded `manual` to `yes` | |
| AC3 | in `lib/sdlc_md.py`, restore `VERIFIED_RE` to demand end-of-line after the optional parenthetical, so an annotated value matches nothing | |
| AC4 | in `verify_ac.py`, treat an unreadable value as an absent line, which inserts a second `Verified:` line above the original | |
| AC5 | in `verify_ac.py`, change the `recorded` default from an empty string to `no`, so an absent `Verified:` line enters the non-positive branch | |
| AC6 | in `verify_ac.py`, insert a write of `Status: Open` over `Status: Done` beside the recorded-not-verified failure | |
| AC7 | in `verify_ac.py`, change the downgrade write from the marked state back to a bare `no`, so the next run cannot tell its own write from an author's | |
| AC7 | in `verify_ac.py`, set `authored` to False so every recorded verdict is read as this tool's own | |
| AC8 | in `lib/sdlc_md.py`, replace the separator lookahead with a word boundary, so `yes-ish` parses as a positive `yes` | |
| AC9 | in `lib/sdlc_md.py`, add `stale` to `VERIFIED_POSITIVE` | |
| AC10 | in `verify_ac.py`, redefine `authored` as `bool(block.verified_reason.strip())` in place of the mark test, which protects none of the 18 bare corpus lines | |
| AC11 | in `verify_ac.py`, hardcode the flip's `old_state` to `none` | |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Filed |
| 2026-09-22 | Claude Opus 5 | Round 3 - the review REJECTed again and ruled round 2's repair MOVED rather than CLOSED, on one measurement that settled it: every one of this corpus's 18 non-positive `Verified:` lines is BARE, so keying protection on a recorded reason protected none of them and left 100% of the real instances being destroyed. The premise that a disclosure can be told from a machine write by reading the line was wrong - the author and `update_verified` write the identical shape. `verify_ac` now MARKS the downgrades it writes, and any unmarked non-positive verdict is read as the author's; marked ones still clear, so the loop closes. The reviewer also refuted my claim that the parser failed safe: `yes-ish` and `yes/no unclear` each parsed as a POSITIVE `yes`, so the boundary is now a real separator and an ambiguous value reaches the unreadable branch. The changelog claim that twelve units would report failing was false under round 2 and is true under round 3. AC6's fixture asserted only the status, so it passed while the run greened the line it was named to protect; it now asserts its branch is reached first. Points 8 to 13. |
| 2026-09-22 | Claude Opus 5 | Round 2 - the delivery review REJECTed and was right twice. It proved by execution that `update_verified` writes `no (<date>)` ITSELF when a stamped-green criterion goes red, and that `git log -S` puts the corpus's dated `no` lines in sprint-close commits rather than in an author's hand - so reading every non-positive verdict as a disclosure made the red-fix-green loop impossible to close. Provenance now decides: a verdict carrying a REASON is the author's and is sticky; a bare dated one is this tool's own downgrade and a green selector clears it. It also proved AC3's second clause false - the recorded reason reached no reader for a POSITIVE value, and the fixture asserted on the file, which a positive verdict never rewrites, so the mutant deleting the capture survived the whole module. The reason now reaches `recorded_reasons` in the report and the fixture asserts there. Three further mutants it ran and found SURVIVING - the word boundary, `stale`'s exclusion, and the reason capture - are now pinned by AC8, AC9 and AC3. Points 5 to 8. |
| 2026-09-22 | Claude Opus 5 | Re-specified against measurement BEFORE any code. The filed summary said a non-`yes` line was treated like `yes`; driving fixtures through the shipped CLI shows two sharper defects - a parsed `no`, `manual` or `stale` is OVERWRITTEN with `yes` by a green selector, and an annotated or out-of-vocabulary value fails `VERIFIED_RE` entirely, after which a second contradictory `yes` is inserted above the original. 17 of 3143 corpus lines sit in that second state. Scope now covers widening the pattern and suppressing the write-through; points 3 to 5, and `lib/sdlc_md.py` joins `Affects`. |
