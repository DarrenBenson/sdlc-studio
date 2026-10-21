# BG1049: BG1044's ruling-record tests leave the date, the note's once-only rule, the heading anchor and the case boundary unpinned

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_record_past_the_cap.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, changelog.d/BG1044.md, changelog.d/BG1049.md
> **Evidence:** BG1044 round-1 QA verdict in sdlc-studio/reviews/critic-verdicts.md (APPROVE, BLOCKING: none): 25 mutants run, 19 killed, the 6 survivors forming the gaps above, each re-tested alone.
> **Created:** 2026-10-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-14T12:05:06Z

## Summary

BG1044's QA seat approved with notes, each executed. (1) AC2's real recorded date is asserted only negatively (recorded != 1999-01-01), so a writer that drops the date or a reader that never reads the last field passes every test. (2) The note's round trip is unpinned: pointing `_RULING_MARK` at text neither the note nor the intro carries, or writing the note before every ruling, passes the module; two rulings into one section then write two notes. (3) The line anchor on the Supersessions heading search is unpinned: an unanchored search passes, though a verdict row quoting the heading would then suppress the section heading. (4) decisions.standing's case fold has no negative boundary: folding after the lineage check passes, and would admit a superseded hand-typed 'Accepted'. (5) `_ruling_value`'s docstring says a newline before recorded= was left live; `_clean` already folded newlines, so only the tab half is true. (6) changelog.d/BG1044.md lists the below-cap note under Fixed, though that behaviour was unchanged and only pinned. (7) pre-existing: the mark is matched anywhere in the section's prose, so a SUPERSEDED record whose reason quotes 'RULING record names' stands in for the note.

## Steps to Reproduce

In `test_critic_record_past_the_cap.py`'s module, replace `sdlc_md.now_date()` in `_append_ruling`'s record with '-': all 8 tests pass.

## Proposed Fix

Assert recorded == today and the reviewer's prefix; record two rulings into one section and assert one note; seed a row quoting the heading with no section yet and assert the heading is written; add a superseded 'Accepted' decision and assert it is refused; correct the docstring and the changelog; match the note's own line rather than the phrase anywhere.

## Acceptance Criteria

- [ ] **AC1** Given a ruling round recorded with a tab-carrying reviewer id, when the record is read back, then its recorded field equals the day it was written.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_record_past_the_cap.py::RecordPastTheCapTests::test_a_tabbed_reviewer_ruling_records_today
- [ ] **AC2** Given two ruling rounds recorded into one section, when the ledger is read, then the section holds exactly one note.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_record_past_the_cap.py::RecordPastTheCapTests::test_two_rulings_into_one_section_write_one_note
- [ ] **AC3** Given a verdict row quoting the Supersessions heading and no section yet, when a ruling is recorded, then the section heading is written; and a superseded decision whose Status reads 'Accepted' does not authorise a round
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_record_past_the_cap.py::RecordPastTheCapTests::test_the_heading_search_is_anchored_and_a_superseded_accepted_is_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-14 | sdlc-studio | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
