# US1148: The PRD leads with human in the lead and its outcomes cite Abena Osei and Graham Doyle

> **Status:** Ready
> **Delivers:** CR0689
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/prd.md, tools/tests/test_lean_prd_refresh.py
> **Epic:** EP0305
> **Points:** 3
> **Depends on:** US1147
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The PRD leads with human in the lead and its outcomes cite Abena Osei and Graham Doyle
**So that** CR0689 is delivered by work that can be planned and checked

## Acceptance Criteria

- **AC1:** Given `sdlc-studio/prd.md`, then the first non-blank line under `## Mission` is `**Human in the lead, not just in the loop.**`, and the Mission's existing paragraphs follow it unchanged. Fails on: the line missing, or placed after the first paragraph.
  - **Verify:** shell awk '/^## Mission$/{m=1;next} m&&NF{print;exit}' sdlc-studio/prd.md | grep -qxF '**Human in the lead, not just in the loop.**'
- **AC2:** Given the PRD's `## Outcomes`, then O10 to O13 follow O9, each a single `- **On:**` line reading word for word: O10 `A change that reaches a change board carries one evidence pack, built from what the run recorded rather than written afterwards and readable without running the tool: what changed, which criteria passed, who reviewed it independently, what is known to be wrong, and the person accountable for it, never 'the agent'; every specification it rests on names its accountable owner the same way (Abena Osei, End goal 1; Abena Osei, End goal 2; Graham Doyle, End goal 1; Graham Doyle, End goal 2)`; O11 `Each team sees what its delivery costs per point, in money, against a monthly budget it declares, whichever harness ran the work (Abena Osei, End goal 3)`; O12 `A defect that escapes to production is traced to the unit and the verdict that let it through, and the next plan, build and review carry what it taught, so the same mistake does not ship twice (Abena Osei, End goal 4; Graham Doyle, End goal 3)`; O13 `The committed record of reports, run records, verdicts and lessons is versioned and complete, so people who never open a terminal follow progress, evidence and cost on the read-only companion dashboard, without the operator's machine or anyone to translate (Abena Osei, End goal 5)`. The test holds the four texts word for word. Fails on: any word changed; an outcome missing or placed before O9; an outcome naming Rowan Achterberg (D0380).
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::OutcomeCitationTests::test_o10_to_o13_read_as_ruled
- **AC3:** Given O5, then it reads `The process stays small enough to serve the work: a repeated failure is fixed in the code path, and a check that catches nothing is deleted (Maya Okafor, End goal 5; Abena Osei, End goal 6)`, and `O5_CITES` in `tools/tests/test_lean_prd_refresh.py` holds the pair `("Maya Okafor", "5")` and `("Abena Osei", "6")`, so O5 citing exactly that pair, in either order, passes. Fails on: O5 citing either End goal alone; O5 re-pointed to another End goal; a third citation beside the pair; a card that no longer states End goal 5 or End goal 6.
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::OutcomeCitationTests::test_o5_and_jonahs_upgrade_goal_are_cited
- **AC4:** Given the outcomes and the cards, then every End goal of Maya Okafor (1 to 5), Jonah Reyes (1 to 4), Abena Osei (1 to 6) and Graham Doyle (1 to 3) is cited by exactly one outcome, and O1 to O4 and O6 to O9 keep their citations. Fails on: O12 losing `Graham Doyle, End goal 3`, so no outcome cites it; O11 also citing `Abena Osei, End goal 1`, so it is cited twice.
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::OutcomeCitationTests::test_every_end_goal_is_cited_once
- **AC5:** Given a temporary root holding copies of `sdlc-studio/prd.md` and `sdlc-studio/personas/`, when `sprint.py plan --root <tmp> --stories Ready --sprint-goal "One evidence pack per change" --serves O10 --no-fetch` runs, then it prints a line starting `goal serves: O10 -` and naming both `Abena Osei` and `Graham Doyle`, and no `goal serves: NONE` line; with O10's line removed from the copy, it prints `the PRD lists no outcome O10` and `goal serves: NONE`. Fails on: O10 missing, or citing neither persona.
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::OutcomeCitationTests::test_a_goal_serving_o10_names_the_primary_and_the_approver
- **AC6:** Given the changed registry and PRD, then `tools/tests/test_persona_coherence.py` and `tools/tests/test_lean_prd_refresh.py` pass in full. Fails on: any test in either module red.
  - **Verify:** shell python3 -m pytest -q tools/tests/test_persona_coherence.py tools/tests/test_lean_prd_refresh.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-09 | Claude Opus 5.5 (run nine grooming) | Acceptance criteria and Verify lines authored at grooming |
| 2026-11-09 | Claude Opus 5.5 (plan approval, D0446) | O10 also names each specification's accountable owner, so it covers all of Abena Osei's End goal 2 (the operator's ruling on the product seat's dissent) |
