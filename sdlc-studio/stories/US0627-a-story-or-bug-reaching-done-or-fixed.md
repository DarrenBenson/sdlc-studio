# US0627: a story or bug reaching Done or Fixed over an unanswered REJECT is refused until its findings are filed or the REJECT is repaired

> **Status:** Done
> **Findings-filed-to:** BG0704
> **Delivers:** CR0526
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0206
> **Points:** 8
> **Persona:** Maya Okafor

## User Story

**As a** reviewer of record
**I want** a story or bug carrying an unanswered REJECT to refuse Done or Fixed until its findings are filed through `critic repair` or the REJECT is completely repaired, as `critic.coverage_state` reads it - a stop-ship ruling holds the close instead (D0194)
**So that** a rejection is answered on the record rather than outlived by the unit that earned it

## Acceptance Criteria

Every fixture below records its REJECT through `critic.record_verdict` in the DELIVERY phase (reviewer `qa`, author `dev`, a brief fingerprint, two findings) and otherwise clears every other gate - no `review.two_role_after`, no `review.test_plan_after`, each criterion verified green - so a refusal is asserted on `unanswered delivery REJECT`, text no other gate emits. The guard is a forceable close gate like its neighbours: every "proceeds" and "refused" case runs WITHOUT `--force`, and AC13 pins what `--force` does. The REJECT is answered exactly when `critic.coverage_state` reads it `approved` (a later same-brief APPROVE) or `repaired` (a complete repair, whose `filed:` closures name artefacts that still resolve).

### AC1: an unanswered delivery REJECT blocks a story's Done

- **Given** a story carrying the delivery REJECT above, with no repair and no later APPROVE
- **When** `transition.py set --status Done` runs WITHOUT `--force`
- **Then** it exits non-zero with the status unchanged, and the refusal carries `unanswered delivery REJECT`, naming the REJECT's reviewer and verdict date
- **Mutant:** stop reading the delivery ledger, or name only the unit
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_recorded_reject_blocks_done
- **Verified:** yes (2026-09-16)

### AC2: and every delivered terminal of a bug, from any status

- **Given** a bug carrying the same unanswered delivery REJECT, with `Verification depth: conversational` (above functional, so the depth gate passes Verified) and not production-affecting (so Closed needs no soak)
- **When** it is set, each WITHOUT `--force`, from In Progress to Fixed, to Verified and to Closed, and from Fixed to Verified and to Closed
- **Then** all five are refused with `unanswered delivery REJECT` - the guard keys on `sdlc_md.is_delivered_terminal`, not on named statuses nor on the status being left, since a bug reaches Verified or Closed without passing Fixed and 16 bugs at Fixed carry an unanswered delivery REJECT
- **Mutant:** gate the story route only, gate Done and Fixed by name, or skip a bug already at Fixed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_recorded_reject_blocks_every_delivered_terminal_for_a_bug
- **Verified:** yes (2026-09-16)

### AC3: findings all filed through `critic repair` discharge it

- **Given** the REJECT's two findings each closed through `critic.py repair` with a `filed:` disposition naming a bug that exists in the fixture, so `critic.coverage_state` reads `repaired`
- **When** `transition.py set --status Done` runs WITHOUT `--force`
- **Then** it exits 0 at Done and prints no `unanswered delivery REJECT` - the finding survives as its own tracked artefact (CR0506's disposition, not a new store)
- **Mutant:** refuse every filed id
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_filed_artefact_id_discharges_the_reject
- **Verified:** yes (2026-09-16)

### AC4: a filed id that stops resolving after it was recorded no longer answers the transition

- **Given** the AC3 fixture built through the shipped `critic.py repair` (whose write-time check accepts the ids because both bugs exist), and one filed bug's file then DELETED
- **When** `transition.py set --status Done` runs WITHOUT `--force`
- **Then** it is refused with `unanswered delivery REJECT`, naming as outstanding the finding the deleted id had closed - a discharge nobody can follow is not one
- **Mutant:** accept any filed id that was accepted at write time
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_an_id_naming_no_artefact_is_refused
- **Verified:** yes (2026-09-16)

### AC5: and no longer answers review-coverage either - the check lives in `critic.repair_state`

- **Given** the AC4 fixture, read once before the delete and once after
- **When** `critic.repair_state` and `critic.coverage_state` read the unit's delivery phase
- **Then** before the delete they read `complete` and `repaired` (the positive control); after it `partial`, with the deleted id's finding in `outstanding`, and `unreviewed` - so review-coverage and conformance, which read the same pair, stop counting it too, not only the write-time check in `record_repair`
- **Mutant:** check resolvability in coverage_state alone, or at write time alone
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::RepairStateResolvesFiledIdsTests::test_a_filed_id_deleted_after_recording_stops_answering_both_readers
- **Verified:** yes (2026-09-16)

### AC6: a filed id resolves through `sdlc_md.find_by_id`, which `corpus_cache` memoises

- **Given** a unit whose repair files three findings to three existing bugs
- **When** `critic.repair_state` reads it inside `sdlc_md.corpus_cache()`
- **Then** a spy on `sdlc_md.find_by_id` sees all three ids and the cache holds its by-id index afterwards - an uncached lookup costs ~33 ms an id, and the corpus's 670 ids cost 22 s on every sweep
- **Mutant:** resolve each id by walking the artefact directories directly
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::RepairStateResolvesFiledIdsTests::test_filed_ids_resolve_through_the_cached_lookup
- **Verified:** yes (2026-09-16)

### AC7: a complete repair answers it with no re-review

- **Given** a delivery REJECT whose two findings were closed through `critic.py repair`, one `fixed:` and one `filed:` to an existing bug, with no re-review recorded, so `critic.coverage_state` reads `repaired` - the answer review-coverage and conformance already give
- **When** `transition.py set --status Done` runs WITHOUT `--force`
- **Then** it exits 0 at Done, read through `critic.coverage_state` (on this corpus it agrees with review-coverage and conformance on all 163 REJECT-carrying units - one reader, L-0408) - otherwise the unit passes the close and then stops at its own Done inside apply-signoff, after the run has closed
- **Mutant:** require a re-review APPROVE as well, or accept only filed closures
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_complete_repair_answers_the_reject_as_review_coverage_does
- **Verified:** yes (2026-09-16)

### AC8: a partly filed REJECT is refused

- **Given** a delivery REJECT with two findings of which only one was closed through `critic.py repair` (`filed:` naming an existing bug), so `critic.repair_state` reads `partial` with one filed closure
- **When** `transition.py set --status Done` runs WITHOUT `--force`
- **Then** it is refused with `unanswered delivery REJECT`, naming the one outstanding finding
- **Mutant:** count any filed closure as an answer
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_partly_filed_reject_is_refused
- **Verified:** yes (2026-09-16)

### AC9: a REJECT retired by a later same-brief APPROVE is answered, and only by the same brief

- **Given** a delivery REJECT followed by an independent APPROVE carrying the REJECT's own brief fingerprint and no repair, so `critic.coverage_state` reads `approved` (21 units are in this state, 10 in flight at Ready); and beside it the same fixture whose APPROVE carries a DIFFERENT fingerprint; and a third whose same-brief APPROVE was recorded by the REJECT's author (reviewer = author), which `critic.coverage_state` reads as `unreviewed` because a self-approval is not independent
- **When** `transition.py set --status Done` runs WITHOUT `--force` on each
- **Then** the same-brief unit exits 0 at Done; the different-brief unit and the self-approved unit are each refused with `unanswered delivery REJECT`, naming the REJECT's reviewer and date - another seat's approval does not retire this seat's rejection, and an author cannot retire a rejection of their own work
- **Mutant:** read every REJECT row directly, or accept any later APPROVE
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_same_brief_approve_answers_the_reject
- **Verified:** yes (2026-09-16)

### AC10: the guard reads the delivery phase only

- **Given** a story whose only REJECT is unrepaired in the PLAN-REVIEW ledger, in a fixture with no `review.test_plan_after` (so the test-plan gate reads nothing); and beside it the same REJECT recorded in the delivery phase
- **When** `transition.py set --status Done` runs WITHOUT `--force` on each
- **Then** the plan-review unit exits 0 at Done and the delivery unit is refused with `unanswered delivery REJECT` - 41 units carry a standing unrepaired plan-review REJECT, and a plan rejection is the plan gate's to answer
- **Mutant:** read the plan-review phase as well
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_plan_review_reject_alone_does_not_block
- **Verified:** yes (2026-09-16)

### AC11: no carried-table ruling discharges a REJECT (D0194)

- **Given** the AC1 fixture, nothing filed, plus a retro whose `Known issues carried` table rules the unit with a ruler and date - once each as `stop-ship`, `not-stop-ship`, `accepted-risk` and `deferred` - and `retro.carried_issues` reading each row back `ok` with that ruling, so a refusal is not a malformed row
- **When** `transition.py set --status Done` runs WITHOUT `--force` under each ruling
- **Then** all four are refused with `unanswered delivery REJECT` - a stop-ship ruling holds the close rather than being the cheapest route to Done, and the other three rule on the close, not on the reviewer's findings
- **Mutant:** let a ruling discharge the REJECT
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_stop_ship_ruling_does_not_discharge_the_reject
- **Verified:** yes (2026-09-16)

### AC12: an abandonment terminal names the REJECT and proceeds

- **Given** a story and a bug each carrying the AC1 unanswered delivery REJECT
- **When** the story is set to Won't Implement and, separately, to Superseded, and the bug to Won't Fix, each WITHOUT `--force`
- **Then** all three exit 0 at the new status and the output carries `unanswered delivery REJECT` with the REJECT's reviewer and date - the code it judged will not ship, so refusing would force filings about work nobody will do, and silence would drop the REJECT from view
- **Mutant:** refuse abandonment too, or say nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_an_abandonment_terminal_names_the_reject
- **Verified:** yes (2026-09-16)

### AC13: `--force` waives the guard and the forced-override record names it

- **Given** the AC1 fixture
- **When** `transition.py set --status Done --force` runs
- **Then** it exits 0 at Done and the artefact's `Forced-override` field and its Revision History row name `unanswered delivery REJECT` among the waived gates - forceable like its neighbours, and visible afterwards on the same terms
- **Mutant:** make the guard unforceable, or check it where `_force_bypassed` cannot re-derive it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_force_waives_the_guard_and_the_record_names_it
- **Verified:** yes (2026-09-16)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/scripts/transition.py, remove the critic.coverage_state read of the unit's delivery verdict before a delivered-terminal transition | an unanswered delivery REJECT blocks a story's Done |
| AC1 | in .claude/skills/sdlc-studio/scripts/transition.py, drop the reviewer and verdict date from the refusal so it names only the unit id | an unanswered delivery REJECT blocks a story's Done |
| AC2 | in .claude/skills/sdlc-studio/scripts/transition.py, add a story-type condition around the unanswered-REJECT guard so a bug skips it | and every delivered terminal of a bug, from any status |
| AC2 | in .claude/skills/sdlc-studio/scripts/transition.py, replace the guard's sdlc_md.is_delivered_terminal test with target_canon in ('Done', 'Fixed') | and every delivered terminal of a bug, from any status |
| AC2 | in .claude/skills/sdlc-studio/scripts/transition.py, skip the guard when from_canon is already a delivered-terminal status | and every delivered terminal of a bug, from any status |
| AC3 | in .claude/skills/sdlc-studio/scripts/critic.py, add every filed-disposition closure to repair_state's outstanding list even when its id resolves | findings all filed through `critic repair` discharge it |
| AC4 | in .claude/skills/sdlc-studio/scripts/critic.py, drop the resolvability check from repair_state so a filed: closure counts whatever its id resolves to | a filed id that stops resolving after it was recorded no longer answers the transition |
| AC5 | in .claude/skills/sdlc-studio/scripts/critic.py, move the resolvability check out of repair_state into coverage_state, leaving repair_state reading complete | and no longer answers review-coverage either - the check lives in `critic.repair_state` |
| AC5 | in .claude/skills/sdlc-studio/scripts/critic.py, remove the find_by_id call on re-read so only record_repair checks ids at write time | and no longer answers review-coverage either - the check lives in `critic.repair_state` |
| AC6 | in .claude/skills/sdlc-studio/scripts/critic.py, replace the sdlc_md.find_by_id call in repair_state with a direct glob of the artefact directories | a filed id resolves through `sdlc_md.find_by_id`, which `corpus_cache` memoises |
| AC7 | in .claude/skills/sdlc-studio/scripts/transition.py, add a later-APPROVE requirement beside the complete-repair test | a complete repair answers it with no re-review |
| AC7 | in .claude/skills/sdlc-studio/scripts/transition.py, skip fixed: closures when counting answers, so only filed: closures discharge the REJECT | a complete repair answers it with no re-review |
| AC8 | in .claude/skills/sdlc-studio/scripts/transition.py, replace the coverage_state read with a test that repair_state's filed count is above zero | a partly filed REJECT is refused |
| AC9 | in .claude/skills/sdlc-studio/scripts/transition.py, refuse on any REJECT row read_verdicts returns whose repair_state is not complete, instead of asking coverage_state | a REJECT retired by a later same-brief APPROVE is answered, and only by the same brief |
| AC9 | in .claude/skills/sdlc-studio/scripts/transition.py, treat any APPROVE recorded after the REJECT as an answer, whatever its brief fingerprint | a REJECT retired by a later same-brief APPROVE is answered, and only by the same brief |
| AC9 | in .claude/skills/sdlc-studio/scripts/transition.py, key the guard's carries-a-REJECT test on critic.verdict_for returning a REJECT instead of on critic.coverage_state, so a same-brief APPROVE the author recorded on their own unit retires the REJECT | a REJECT retired by a later same-brief APPROVE is answered, and only by the same brief |
| AC10 | in .claude/skills/sdlc-studio/scripts/transition.py, call coverage_state for phase plan-review as well as delivery and refuse when either reads unreviewed | the guard reads the delivery phase only |
| AC11 | in .claude/skills/sdlc-studio/scripts/transition.py, add the retro carried table's stop-ship rulings to the answers accepted for a REJECT | no carried-table ruling discharges a REJECT (D0194) |
| AC11 | in .claude/skills/sdlc-studio/scripts/transition.py, add not-stop-ship, accepted-risk and deferred rows from retro.carried_issues to the accepted answers | no carried-table ruling discharges a REJECT (D0194) |
| AC12 | in .claude/skills/sdlc-studio/scripts/transition.py, change the abandonment-terminal branch to raise the same refusal the Done branch raises | an abandonment terminal names the REJECT and proceeds |
| AC12 | in .claude/skills/sdlc-studio/scripts/transition.py, return from the guard before the warning for a decision-terminal target so an abandonment prints nothing | an abandonment terminal names the REJECT and proceeds |
| AC13 | in .claude/skills/sdlc-studio/scripts/transition.py, raise the unanswered-REJECT refusal whatever force says so --force cannot waive it | `--force` waives the guard and the forced-override record names it |
| AC13 | in .claude/skills/sdlc-studio/scripts/transition.py, move the check out of _pre_write_gates into set_status behind if not force, so _force_bypassed never re-derives it | `--force` waives the guard and the forced-override record names it |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-15 | sdlc-studio | Retitled: was 'closing a story over a recorded REJECT requires a filed artefact id or an explicit stop-ship ruling' |
| 2026-09-15 | sprint planning 2026-09-15 | Re-groomed at the sprint goal review (round 1: all three seats refused a goal carrying CR0526) against D0193 (an unfinished unit feeds the close's stop-ship step, not a third gate) and D0194 (one stop-ship store, the retro's carried table). Widened to bugs and Fixed (16 of 20 batch units are bugs); a stop-ship ruling no longer discharges a REJECT; CR0506's filed: disposition is the discharge; a repaired-and-re-approved REJECT is the paired control; abandonment terminals name the REJECT. 3 -> 5 points. |
| 2026-09-15 | sprint planning 2026-09-15 | Goal review round 2 repairs: keys on the delivered-terminal set (a bug reaches Verified or Closed without passing Fixed); a complete repair with no re-review answers the REJECT through the same predicate review-coverage uses - requiring re-approval would have moved the close deadlock into apply-signoff. |
| 2026-09-15 | sprint planning 2026-09-15 | Goal review round 3 repairs: the answered-REJECT reader is critic.coverage_state; the filed-id resolvability check moves into critic.repair_state so review-coverage and the transition cannot disagree; the 're-approved' wording that contradicted AC5 is gone. |
| 2026-09-15 | sprint planning 2026-09-15 | Goal review round 4 notes (all three seats YES): AC5 adds a partly-filed REJECT, refused; AC4's check resolves through corpus_cache; test_critic.py joins Affects so the repair_state half is pinned where it lives. |
| 2026-09-15 | sprint plan repair 2026-09-15 | Plan review r1 (QA REJECT) repairs: 7 criteria become 13 with 22 mutant rows. Every fixture records its REJECT in the DELIVERY phase and asserts 'unanswered delivery REJECT', text no other gate emits; every proceeds and refused case runs without --force, and AC13 pins that --force waives the guard and the Forced-override record names it. AC2 now covers Fixed, Verified and Closed from In Progress and from Fixed, with conversational depth, plus a named-status mutant. AC3's mutant moves into critic.repair_state. AC4 builds its fixture through critic repair and then deletes the filed bug; AC5 pins the same in test_critic.py for repair_state and coverage_state with a before-delete control; AC6 pins resolution through sdlc_md.find_by_id under corpus_cache. AC8 refuses a partly filed REJECT; AC9 answers a same-brief APPROVE with a different-brief control; AC10 reads the delivery phase only; AC11 refuses under all four carried-table rulings; AC12 names the REJECT without refusing across Won't Implement, Superseded and Won't Fix. |
| 2026-09-15 | sprint plan repair 2026-09-15 | Re-sized 5 -> 8 points (the split ceiling) after the plan repair grew it from 7 criteria to 13 and 22 mutant rows. |
| 2026-09-15 | sprint plan repair 2026-09-15 | Plan round 2 repair: AC9 adds a third fixture - a same-brief APPROVE the REJECT's author recorded, read unreviewed by coverage_state and refused - with the mutant that keys the guard on critic.verdict_for instead. |
| 2026-09-15 | delivery repair 2026-09-15 | Delivery review r1 (QA and engineering REJECT) repairs. critic.standing_rejects no longer hand-copies verdict_for's supersession rule: both read one filter, critic._live_verdict_rows, pinned through transition.py set by an author-superseded REJECT (refused) beside a principal-superseded one (lands). The refusal names every unanswered REJECT and no answered one, and a REJECT itemising no findings no longer claims every finding carries a closure. Affects widens to sprint.py and tests/test_sprint.py: the close pre-flight and the apply-signoff fan-out moved every batch story and bug to Done, abandoned units included, so an abandoned unit with an unanswered delivery REJECT stopped the close at the new guard. They now skip a unit already at an abandonment terminal (read through sdlc_md.is_terminal_status and is_delivered_terminal) and apply-signoff names each one it skips. |
