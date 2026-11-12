# US1147: Graham Doyle joins the registry as Served and Trevor Hale narrows to what the skill declines

> **Status:** Ready
> **Delivers:** CR0689
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/personas/graham-doyle-change-approver.md, sdlc-studio/personas/trevor-hale-enterprise-pm.md, sdlc-studio/personas/index.md, sdlc-studio/prd.md, tools/tests/test_persona_coherence.py, changelog.d/US1147.md
> **Epic:** EP0305
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** Graham Doyle joins the registry as Served and Trevor Hale narrows to what the skill declines
**So that** CR0689 is delivered by work that can be planned and checked

## Acceptance Criteria

- **AC1:** Given `sdlc-studio/personas/graham-doyle-change-approver.md`, then it is headed `# Graham Doyle`; its Quick Reference rows read Cast role `Served`, Role `Chairs the change approval board in an audited organisation` and Context `Approves each release from the evidence put in front of him; never runs the tool or opens a terminal`; it carries no `Interface` row; and its `## End Goals` are these three, in order, each on one line: 1 `Approve a change from one document showing what changed, which criteria passed, who reviewed it independently, what is known to be wrong, and who is accountable`; 2 `Trust that the evidence came from the process, not written after the fact`; 3 `See fewer surprises in production over time`. The test holds the three word for word. Fails on: an End goal reworded, reordered, wrapped onto a second line or missing; a Cast role other than Served; an `Interface` row.
  - **Verify:** pytest tools/tests/test_persona_coherence.py::ServedAndNegativeTests::test_the_change_approvers_card_states_the_three_ruled_end_goals
- **AC2:** Given the persona cards, then Graham's card carries the sections a Served card needs (Quick Reference, Who They Are, End Goals, Behaviours & Context, Frustrations; Experience Goals and Scenario optional) and `validate.py personas` reports nothing for the cast. Fails on: a required section missing from his card.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::PersonaWellFormedTests::test_shipped_personas_are_well_formed
- **AC3:** Given the index and the PRD, then the index carries `## Served (affected by the product without using it)` between `## Secondary` and `## Negative`, listing `- [Graham Doyle](graham-doyle-change-approver.md) - chairs the change approval board; approves a release from the evidence it carries and never runs the tool (D0437).`; `ROLES` in `tools/tests/test_persona_coherence.py` includes `Served` and the derived-names fixture parses a Served entry; and `### Target Users` gains, after the Secondary bullet, `**Served (affected by the product without using it):** Graham Doyle, who chairs the change approval board and approves a release from the evidence it carries, without running the tool.` Fails on: Graham left out of Target Users while the index lists him; `Served` missing from `ROLES`, so the check reads past him.
  - **Verify:** pytest tools/tests/test_persona_coherence.py::PrdTargetUsersTests
- **AC4:** Given a temporary root holding copies of `sdlc-studio/prd.md` and `sdlc-studio/personas/`, when `sprint.py plan --root <tmp> --stories Ready --sprint-goal "Approve a release from one document" --serves "Graham Doyle" --no-fetch` runs, then it prints `goal serves: Graham Doyle (Served)` and no `goal serves: NONE` line; the same command with `--serves "Trevor Hale"` prints `goal serves: NONE`. Fails on: Graham's card missing or its Cast role not Served; the Trevor control not printing NONE.
  - **Verify:** pytest tools/tests/test_persona_coherence.py::ServedAndNegativeTests::test_a_goal_serving_the_change_approver_is_not_flagged
- **AC5:** Given Trevor's card, then its `## End Goals (stated to exclude)` are exactly these four, in order: 1 `Drive delivery from a rich GUI with boards, swimlanes, and portfolio dashboards`; 2 `Enforce multi-stage human approval and sign-off gates on every change`; 3 `Have non-technical staff operate the tool`; 4 `Sync the work to Jira, Azure Boards or another enterprise tracker`; its Quick Reference Role reads `GUI-first delivery manager` and Context `Runs delivery from a GUI work-tracker and wants non-technical staff operating the tool and a human approval on every change`; its `## Why We Are Not Designing For Him` names Abena Osei, not Maya, as the Primary those wants would cost, and says audit evidence and the running of several teams are served through her (D0436); the index's Trevor bullet reads `- [Trevor Hale](trevor-hale-enterprise-pm.md) - a GUI-first operator wanting non-technical staff to run the tool and a human approval on every change. A signal to decline, not a backlog. Well-formed.` and the PRD's Negative bullet reads `**Negative (deliberately not designed for):** Trevor Hale, a GUI-first operator wanting non-technical staff to run the tool and a human approval on every change. A signal to decline, not a backlog.`; D0213, `sprint.py sign` and the links to each Primary's card stay. Fails on: a fifth excluded End goal left (SSO and compliance reporting from the corporate stack, or governing many teams centrally); tracker sync missing from the excluded End goals; his card naming Maya as the Primary; the index or the PRD still saying central governance.
  - **Verify:** pytest tools/tests/test_persona_coherence.py::ServedAndNegativeTests::test_trevor_is_narrowed_to_the_three_wants_the_skill_declines
- **AC6:** Given the index's Revision History, then it gains a row dated the day it is committed whose Change reads `Graham Doyle added as Served, the change approver (D0437); Trevor Hale narrowed to a GUI-first operator, non-technical staff running the tool and a human approval on every change (D0436)`; the rows stay in date order and `Last updated` equals the latest row's date. Fails on: no row for the commit's date; a row out of date order.
  - **Verify:** pytest tools/tests/test_persona_coherence.py::RegistryRecordTests
- **AC7:** Given Trevor's `## Scenario`, then it no longer points him at an enterprise tool that fits: it points his wants for boards and dashboards at the read-only companion dashboard over the committed record (RFC0063 D6), and still declines a human approval on every change, non-technical staff running the tool and sync to an enterprise tracker. Fails on: the Scenario still naming an enterprise tool; the companion dashboard named as anything but read-only; any of the three declined wants offered.
  - **Verify:** pytest tools/tests/test_persona_coherence.py::ServedAndNegativeTests::test_trevors_scenario_points_boards_and_dashboards_at_the_read_only_companion_dashboard

## Redelivery note (run ten)

Checked at HEAD 508e2408 against the verdict ledger.

- **The REJECT's one BLOCKING finding is answered.** The REJECT is qa-seat-US1147-r1's round 2 (`sdlc-studio/reviews/critic-verdicts.md:1838`, brief 783a0b3628d5). Its BLOCKING finding was that the AC7 test's `CLAUSE_TURN` word list let a declined want offered inside the declining clause pass ("is offered", "ships", "gives him", "declines none of", "declines, then accepts"). BG1318 (Fixed, 897b4c63) replaced that list with `DECLINING_REST` (`tools/tests/test_persona_coherence.py:210`, asserted at `:983`). qa-seat-BG1318-r1 approved it (`critic-verdicts.md:1839`, brief 10373ae44eec), re-running all six round-2 mutants and both round-1 mutants, and every one now fails. The REJECT's other finding, Jonah Reyes's line, is item (3) of open BG1314 and does not hold this unit.
- **No criterion has moved since.** qa-seat-BG1318-r1 ran the persona coherence module and `PersonaWellFormedTests` at 897b4c63: 53 passed. Since then, only US1148's 77edb628 has touched this unit's files. It edited other parts of `sdlc-studio/prd.md`, and the Served and Negative bullets AC3 and AC5 pin are unchanged at `prd.md:197-202`. No later commit touches the persona reader or `sprint.py plan --serves`.
- **The author self-check is current.** It was recorded at c4d53913, and `critic.self_check_gap` finds it current, because the own-change view sets BG1318's and US1148's commits aside as other units' work. `critic.py brief --rejoinder` is therefore not refused under `review.author_self_check: block`.
- **The redelivery is the rejecting seat's next round only.** No builder change is needed. Brief the seat with `critic.py brief --unit US1147 --seat qa --rejoinder <file>`, where the file holds row 1838's verdict as a VERDICT, ISSUES and BLOCKING block. `critic.py show --unit US1147` prints that row as a record, not as such a block. Record the verdict with `critic.py record`. As in D0433, Done follows that seat's APPROVE.
- **One gap is left, which the seat reports rather than blocks on.** BG1321 (Open, Low, 1 point) records two gaps that this unit's own repair c4d53913 brought in. First, the check for a want named outside the declining clause is case-sensitive (`:988`), so a Scenario that appends "Sync to an enterprise tracker is offered." passes AC7. Second, `NEGATION` is a word list (`:212`, asserted at `:979`), so "seldom declines" passes. As a result, `changelog.d/US1147.md:14-17` claims more than the test holds. BG1321's Affects lie inside this unit's. Because the gap is recorded in an open bug, the seat reports it by id rather than blocking on it. Landing BG1321 before the rejoinder would remove the one claim the seat could still find over-stated.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-09 | Claude Opus 5.5 (run nine grooming) | Acceptance criteria and Verify lines authored at grooming |
| 2026-11-09 | Claude Opus 5.5 (plan approval, D0446) | Trevor keeps sync to an enterprise tracker as an excluded End goal, and his Scenario points boards and dashboards at the read-only companion dashboard (the operator's rulings at plan approval) |
| 2026-11-09 | Claude Opus 5.5 (run nine) | Affects names the unit's changelog fragment, which grooming left out |
| 2026-11-12 | Claude Opus 5.5 (engineering seat) | Re-groomed at HEAD for run ten: redelivery note added (BG1318 answers the round-2 REJECT's blocking finding, every criterion still holds, the self-check is current, so the redelivery is qa-seat-US1147-r1's rejoinder round alone; BG1321 is the residual); criteria, Affects and Points unchanged |
