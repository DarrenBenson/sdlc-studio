# BG0261: The state anchor and the goal verdict both describe three review rounds when ten happened, and the freshness check that exists for exactly this only counts lines

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/doc_freshness.py,.claude/skills/sdlc-studio/scripts/lib/run_state.py,.claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py,.claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Found while planning the sprint AFTER RUN-01KY3MFX, by reading the anchor the doctrine says to read first. Two surfaces are wrong in the same direction and neither is checked.

LATEST.md still says the run is 'NOT closed', that 'round 3's repair is UNREVIEWED and the sign-off is owed', and that five rounds have run. In fact all 23 stories are Done, `close_owed` detect reports none, the run carries a recorded close attempt with a sign-off stage, and the closing artefacts (CR0402, CR0404) describe TEN adversarial rounds. A fresh context following the anchor would go looking for an owed signature that landed and an unreviewed repair that was reviewed five more times.

The recorded `sprint_goal_verdict` note has the same defect and less excuse: it says 'three independent adversarial rounds' and 'Round 3 REJECTED with three MAJORs'. Rounds 1 to 5 were already recorded in the SAME JSON object when that note was written. The data to contradict the prose sat in the adjacent key.

The round ledger is itself incoherent. run-state.json holds six `review_rounds` entries for a loop the close describes as ten, so rounds 8, 9 and 10 were never recorded at all. Entry round 6 carries a reviewer string reading 'round 7', so the tool's own numbering and the reviewer's disagree by one and nothing objects. Entry 6 was recorded at 12:14:27Z against a run whose `ended_at` is 11:41:23Z - a review round accepted against a run already ended, silently.

`doc_freshness.py` exists for precisely this failure. Its own docstring says LATEST.md 'drifts silently' and that it 'compares the facts LATEST.md claims against reality'. Run today it reports one finding: that the file is 101 lines against an 80-line ceiling. It checks version string, test count, disclosure count and length. It does not check the two claims that are load-bearing for an agent resuming work - whether a sign-off the document says is owed has landed, and whether the round count it narrates matches the run's own ledger. Both are one comparison against state the tool already holds.

This is the same class as BG0257 and the surviving MAJOR of nine consecutive closing reviews: prose asserting a property the data does not have, with the contradicting data present and unread. It is worse here in one respect - this is the document written specifically to stop a fresh context believing something false.

## Steps to Reproduce

1. Read sdlc-studio/reviews/LATEST.md: it states the run is not closed and the sign-off is owed. 2. Run scripts/`close_owed.py` detect: 'close owed: none'. 3. Check the batch: all 23 stories US0288-US0310 are Done in stories/_index.md. 4. Read `sprint_goal_verdict.note` in sdlc-studio/.local/run-state.json: it says 'three independent adversarial rounds'; read `review_rounds` in the same file: six entries, the last labelled round 7 by its reviewer, recorded 33 minutes AFTER `ended_at.` 5. Run scripts/`doc_freshness.py`: one finding, about line count. Expected: the freshness check reports the claimed-but-landed sign-off and the round-count divergence; the verdict note is refused or flagged when it names a round count the ledger contradicts; a round recorded after `ended_at` is refused or warned.

## Proposed Fix

Three separate small changes, in value order. (1) `doc_freshness` gains two checks against state it can already read - a sign-off or closure LATEST.md claims is outstanding when `close_owed`/the index say otherwise, and a round count narrated in LATEST.md that the run ledger contradicts. (2) The goal-verdict note is cross-checked against len(`review_rounds)` at record time, in the manner of CR0394: do not restate the round count beside the ledger, derive it from the ledger or refuse a note that names a different one. (3) `record_review` refuses, or at minimum warns, when a round is recorded against a run that already carries `ended_at`, and stops accepting a reviewer-supplied round label that disagrees with the index it is stored at. Do not fix this by rewriting LATEST.md by hand: the document being wrong is the symptom, the absent check is the bug, and correcting the prose without the check is exactly the move this project keeps finding in its own reviews.

## Acceptance Criteria

The fix is complete when the two surfaces that carried the false claims are checked
against the state that already contradicts them, and neither check can be satisfied by
correcting the prose: `doc_freshness` reports a sign-off or closure LATEST.md calls
outstanding once the index and `close_owed` say it landed, and reports a round count the
document narrates that the run ledger contradicts; and the round ledger itself refuses
to be contradicted at record time, so a verdict note naming a round count other than
`len(review_rounds)`, a round recorded against a run already carrying `ended_at`, and a
reviewer label disagreeing with the index it is stored at are each refused or reported
rather than written silently. Both tests below fail today: the first because
`doc_freshness` checks only version, test count, disclosure count and length, the second
because nothing reads the ledger back at record time.

### AC1: the freshness check compares the anchor's two load-bearing claims against state

- **Given** a LATEST.md stating that a sign-off is owed and narrating three review
  rounds, over a run whose index shows the batch Done, whose `close_owed` detect reports
  none, and whose `review_rounds` holds six entries
- **When** `doc_freshness` runs
- **Then** it reports both the landed-but-claimed-owed sign-off and the round-count
  divergence as findings, distinct from the line-count finding, and reports neither when
  the document agrees with the state
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py::AnchorClaimsCheckedAgainstRunStateTests::test_a_landed_signoff_and_a_contradicted_round_count_are_both_reported

### AC2: the round ledger cannot be contradicted at the moment it is written

- **Given** a run carrying six recorded rounds and an `ended_at`
- **When** a goal-verdict note naming a different round count is recorded, a round is
  recorded after `ended_at`, and a round is recorded with a reviewer label disagreeing
  with its own index
- **Then** each is refused or reported at that moment, and the round count a note carries
  is derived from the ledger rather than restated beside it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::ReviewLedgerHonestyTests::test_a_note_round_or_label_contradicting_the_ledger_is_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Filed |
