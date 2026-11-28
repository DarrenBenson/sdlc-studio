# US1352: sprint lane brief relays each seat's reply to the builder, and this repository seats a three-member approach panel

> **Status:** Ready
> **Risk-class:** high
> **Delivers:** CR0757
> **Created:** 2026-11-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, sdlc-studio/.config.yaml, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_solution_review_panel_relay.py, .claude/skills/sdlc-studio/scripts/tests/test_one_identity_brief.py, changelog.d/US1352.md, docs/existing-users.md
> **Epic:** EP0386
> **Points:** 2
> **Depends on:** US1294, US1342, US1346, US1347, US1348, US1350, US1351
> **Persona:** Abena Osei

## User Story

As an engineering lead, I want the builder's brief to show every seat's reply by seat and round and the run report to count a unit's rounds as rounds, so that no plan one seat still rejects is built and the change board reads the step's figures as the run produced them.

## Acceptance Criteria

### AC1: a mixed round is relayed seat by seat and never reads as agreed

- **Given** `review.solution_review.min_points: 2` and `panel: [qa, product, persona]`, a 3-point
  story whose Persona is Abena Osei, qa CHANGES with two numbered items and product GO at round 1,
  and no persona verdict
- **When** `sprint.py lane brief --units <id>` is run
- **Then** its solution review block names each seat in panel order: qa's CHANGES at round 1 with
  both items quoted as `>` lines, product's GO at round 1, and Abena Osei (persona) awaiting a
  review; it does not say the approach is agreed; and it tells the builder to revise the note,
  answering each numbered item under the heading it changes and naming the seat and item, to write
  HANDOFF.md and to hand back HANDOFF
- **Fails on:** HEAD plus US1344, whose lane brief for this unit, with the panel set and three rows
  recorded, has 70 lines and 0 naming an approach, a solution review or a panel (E7); and US1346 as
  its approach note plans it reads the unit's last row only
  (`critic.read_solution_reviews(root, uid)[-1]`, E16), under which product's GO after qa's CHANGES
  would read as agreed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_panel_relay.py::SolutionReviewPanelRelayTests::test_a_mixed_round_is_relayed_seat_by_seat

### AC2: the brief says agreed only when every seat has a GO on one note text

- **Given** the same story, then the note revised with qa GO at round 2 while product's and the
  persona's GO stand on the first note, then product and the persona GO on the revised note
- **When** the lane brief is printed after each
- **Then** after the first it names product's and the persona's GO as recorded against the earlier
  digest, asks for them again and does not say agreed; after the second it says the approach is
  agreed, naming each seat's round and the one digest, tells the builder to build to it, and says
  that editing the note voids every GO
- **Fails on:** HEAD plus US1344, whose lane brief has 0 lines naming a solution review (E7)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_panel_relay.py::SolutionReviewPanelRelayTests::test_the_brief_says_agreed_only_on_one_note_text

### AC3: an unset panel keeps the one-seat brief, this repository seats the panel, and help says what it does

- **Given** the same story with the panel unset and one GO recorded, this repository's
  sdlc-studio/.config.yaml, and help/sprint.md's Lanes section
- **When** the lane brief is printed, again with `critic.panel_state` patched to raise; `config.py
  show --key review.solution_review.panel` is run on this repository; and the help page is read
- **Then** the two briefs are byte-equal, so an unset panel is never read and US1346's one-seat block
  stands; this repository reads `[qa, product, persona]`; the relayed brief of AC1, given a qa reply
  that itself holds "You are the qa review seat", reads exactly one identity in
  `test_one_identity_brief`; and the Lanes section has one sentence naming
  `review.solution_review.panel`, saying each seat on it is its own agent and its own review, and
  that the approach is agreed only when every seat has a GO on the note as it stands
- **Fails on:** HEAD, where on this repository `config.py show --key review.solution_review.panel`
  printed "config: no key ..." and exited 1 (E4), and help/sprint.md has 0 matches for
  `solution_review.panel` or "solution review" (E11)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_panel_relay.py::SolutionReviewPanelRelayTests::test_an_unset_panel_keeps_the_one_seat_brief_and_this_repository_seats_the_panel

### AC4: the run report counts a unit's solution review rounds as its highest round

- **Given** a fixture run under `panel: [qa, product, persona]` holding two units that took the
  solution review: one whose three seats GO at round 1 (3 rows), and one with qa CHANGES and product
  GO at round 1, the note revised, then qa, product and the persona GO on it (5 rows, the highest
  Round cell 2)
- **When** `sprint_report.build_report(root, retro_id)` is run and the `solution_review` section's
  took row is read
- **Then** `sr_solution_rounds` reads 1.5 for the two units (1.0 for the first alone, 2.0 for the
  second alone, never 3.0 or 5.0), rounds per unit being each unit's highest Round cell
- **Fails on:** HEAD and HEAD plus US1344, where the report has no `solution_review` section (14
  sections, E15); and US1348 as its approach note plans it: "Solution review rounds per unit count
  its rows (one seat a round)" (E16), which reads 4.0 here (3.0 and 5.0 alone)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_panel_relay.py::SolutionReviewPanelRelayTests::test_the_report_counts_a_unit_s_highest_round

## Notes

- Depends on: S3 (test_one_identity_brief.py; the persona brief must exist before this repository
  seats `persona`), S2 (`panel_state`), US1346 (sprint.py's solution review block), US1347
  (sdlc-studio/.config.yaml, help/sprint.md), US1348 (the report section AC4 reads), US1294 and
  US1342 (help/sprint.md).
- Persona: Abena Osei, End goal 1: "Every release passes the change board on the evidence the run
  produced, with no separate write-up".
- Ran: the lane brief at HEAD plus US1344 with the panel set and rows recorded (E7), the in-flight
  notes (E16), the config probe on this repository (E4), the help grep (E11), the report sections
  (E15).
- AC4 is a pin on US1348's count; S4 adds no report code. If US1348 lands counting rows, S4's
  builder hands back BLOCKED naming sprint_report.py, and the fix is a unit of its own.
- Add the relayed lane brief, with a reply quoting an identity sentence, to
  `test_one_identity_brief.GENERATORS`.
- The brief reads the ledger, never the note (it does not know the lane's worktree), so "on one
  note text" is judged by the GO rows sharing one digest, the latest row's digest being the note's
  latest text; the fragment says so.
- Only the `panel` line of sdlc-studio/.config.yaml changes. If D0647's bar is unmet once measured,
  the first narrowing is to `[qa]` (ruling 3).
- Readers beside the new module: sprint.py is read by 262 modules; test_lane_builder_brief and
  test_lean_lane_brief_repair_scope assert named lines of the brief and never its length, and
  US1346's module holds its one-seat block, which AC3 keeps byte-equal; sdlc-studio/.config.yaml is
  read by tools/tests/test_lean_carry_severity_bar and the v6.5 release tests, none for this key;
  help/sprint.md is named by 21 modules, and help pages carry no line budget (E17, E18).
- In this run BG1765, BG1771 and US1347 also edit .config.yaml, and US1335, US1336, BG1765 and
  US1346 edit sprint.py: S4 follows their lands.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-27 | engineering seat; product seat (D0648) | Groomed for run twenty-eight from the CR0757 breakdown: engineering draft with the product seat's six rulings and changes C1-C23 folded in |
