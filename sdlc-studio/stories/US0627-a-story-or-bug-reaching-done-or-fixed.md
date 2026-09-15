# US0627: a story or bug reaching Done or Fixed over an unanswered REJECT is refused until its findings are filed or the REJECT is repaired

> **Status:** Ready
> **Delivers:** CR0526
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0206
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** reviewer of record
**I want** a story or bug carrying an unanswered REJECT to refuse Done or Fixed until its findings are filed through `critic repair` or the REJECT is completely repaired, as `critic.coverage_state` reads it - a stop-ship ruling holds the close instead (D0194)
**So that** a rejection is answered on the record rather than outlived by the unit that earned it

## Acceptance Criteria

### AC1: an unanswered REJECT blocks a story's Done

- **Given** a story with a recorded REJECT and no answer to it
- **When** `transition.py set --status Done` runs
- **Then** it is refused, naming the REJECT
- **Mutant:** stop reading recorded REJECT verdicts - the guard has nothing to refuse on
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_recorded_reject_blocks_done

### AC2: and a bug's Fixed

- **Given** a bug with a recorded, unanswered REJECT
- **When** it is set to Fixed
- **Then** it is refused on the same terms, and so is Verified or Closed reached directly - the guard keys on the delivered-terminal set (`sdlc_md.is_delivered_terminal`), not on named statuses, since a bug can reach Verified without passing Fixed
- **Mutant:** gate the story route only
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_recorded_reject_blocks_every_delivered_terminal_for_a_bug

### AC3: a finding filed through `critic repair` discharges it

- **Given** the REJECT's findings closed with `filed:` dispositions naming an existing artefact
- **When** the transition runs
- **Then** it proceeds - the finding survives as its own tracked artefact (CR0506's disposition, not a new store)
- **Mutant:** refuse every filed id
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_filed_artefact_id_discharges_the_reject

### AC4: an id naming no artefact is refused

- **Given** a `filed:` disposition whose id names nothing that exists
- **When** the transition runs
- **Then** it is REFUSED - a discharge nobody can follow is not one - and the resolvability check lives in `critic.repair_state`, which review-coverage also reads, so an id that stops resolving after it was recorded stops answering for BOTH readers rather than only at write time - resolved through `corpus_cache`, since an uncached lookup costs ~33 ms an id (670 ids: 22 s)
- **Mutant:** accept any non-empty id
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_an_id_naming_no_artefact_is_refused

### AC5: a completely repaired REJECT answers it, with no re-review - read through `critic.coverage_state`

- **Given** a REJECT whose findings were all closed through `critic repair` - with no re-review recorded - the answer review-coverage and conformance already give; and separately a REJECT with only SOME findings filed
- **When** the transition runs
- **Then** the complete repair proceeds and the partial filing is refused, both read through `critic.coverage_state` (on this corpus it agrees with review-coverage and conformance on all 163 REJECT-carrying units - one reader, L-0408) - otherwise the unit passes the close and then stops at its own Done inside apply-signoff, after the run has closed
- **Mutant:** require a re-review APPROVE as well as the repair - the two readers disagree and the close deadlocks one step later
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_complete_repair_answers_the_reject_as_review_coverage_does

### AC6: a stop-ship ruling does NOT discharge a REJECT (D0194)

- **Given** the REJECT's finding ruled stop-ship in the retro's carried table, nothing filed
- **When** the transition runs
- **Then** it is refused - a stop-ship ruling holds the close; it is not the cheapest route to Done
- **Mutant:** let the ruling discharge the REJECT
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_stop_ship_ruling_does_not_discharge_the_reject

### AC7: an abandonment terminal names the REJECT instead of refusing

- **Given** a unit with an unanswered REJECT
- **When** it is set to Won't Implement, Superseded or Won't Fix
- **Then** the transition proceeds and names the unanswered REJECT - the code it judged will not ship, so refusing would force filings about work nobody will do
- **Mutant:** refuse abandonment too, or say nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_an_abandonment_terminal_names_the_reject

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-15 | sdlc-studio | Retitled: was 'closing a story over a recorded REJECT requires a filed artefact id or an explicit stop-ship ruling' |
| 2026-09-15 | sprint planning 2026-09-15 | Re-groomed at the sprint goal review (round 1: all three seats refused a goal carrying CR0526) against D0193 (an unfinished unit feeds the close's stop-ship step, not a third gate) and D0194 (one stop-ship store, the retro's carried table). Widened to bugs and Fixed (16 of 20 batch units are bugs); a stop-ship ruling no longer discharges a REJECT; CR0506's filed: disposition is the discharge; a repaired-and-re-approved REJECT is the paired control; abandonment terminals name the REJECT. 3 -> 5 points. |
| 2026-09-15 | sprint planning 2026-09-15 | Goal review round 2 repairs: keys on the delivered-terminal set (a bug reaches Verified or Closed without passing Fixed); a complete repair with no re-review answers the REJECT through the same predicate review-coverage uses - requiring re-approval would have moved the close deadlock into apply-signoff. |
| 2026-09-15 | sprint planning 2026-09-15 | Goal review round 3 repairs: the answered-REJECT reader is critic.coverage_state; the filed-id resolvability check moves into critic.repair_state so review-coverage and the transition cannot disagree; the 're-approved' wording that contradicted AC5 is gone. |
| 2026-09-15 | sprint planning 2026-09-15 | Goal review round 4 notes (all three seats YES): AC5 adds a partly-filed REJECT, refused; AC4's check resolves through corpus_cache; test_critic.py joins Affects so the repair_state half is pinned where it lives. |
