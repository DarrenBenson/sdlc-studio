# US1351: critic.py approach panel names one brief and one reply file per seat, and approach brief frames the unit's stakeholder persona

> **Status:** Done
> **Risk-class:** high
> **Delivers:** CR0757
> **Created:** 2026-11-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/scripts/tests/test_solution_review_panel_brief.py, .claude/skills/sdlc-studio/scripts/tests/test_one_identity_brief.py, changelog.d/US1351.md
> **Epic:** EP0386
> **Points:** 3
> **Depends on:** US1345, US1347, US1349, US1350
> **Persona:** Abena Osei

## User Story

As an engineering lead whose team turns on the solution review, I want the tool to name one brief per seat and frame the unit's persona, so that each view of the plan is one named seat's or persona's and none is written by hand.

## Acceptance Criteria

### AC1: the panel names one brief and one reply file per seat

- **Given** `review.solution_review.panel: [qa, product, persona]` and `min_points: 3`, a 3-point
  story whose Persona is Abena Osei, a note, and a qa CHANGES recorded at round 1
- **When** `critic.py approach panel --unit <id> --note <path>` is run, and again with the panel
  unset
- **Then** stdout has one line per seat in panel order: Sam Eriksson (qa) at round 2, Lena Marsh
  (product) at round 1 and Abena Osei (persona) at round 1, each with its `critic.py approach brief
  --unit <id> --seat <seat> --note <path>` command, its latest verdict and its reply file
  `sdlc-studio/.local/solution-review/<key>-<seat>-r<round>.md`; then that each brief goes to its own
  agent and never two in one brief; that a seat's next round resumes that seat's own agent where the
  host can, and otherwise briefs a fresh agent for that seat; that a reply reaches the builder
  through `sprint.py lane brief --units <id>`; that the approach is agreed when every seat has a GO
  on the note's digest now; and that the agent that reviewed the approach does not review the code;
  it names no `SendMessage`, `subagent_type` or `Task(`, and leaves the tree byte-equal; with the
  panel unset it says one seat's GO agrees the approach and names the one-seat brief form
- **Fails on:** HEAD plus US1344, where `critic.py approach panel` is an invalid choice (E5)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_panel_brief.py::SolutionReviewPanelBriefTests::test_the_panel_names_one_brief_and_one_reply_file_per_seat
- **Verified:** yes (2026-11-28)

### AC2: the stakeholder brief frames the persona from its card and no seat

- **Given** the same story, registry and panel, and a second story whose Persona is Rowan Test, a
  registered card built from `templates/personas/persona-template.md`
- **When** `critic.py approach brief --unit <id> --seat persona --note <path>` is run for each, and
  `--seat qa` for the first
- **Then** each persona brief opens by telling its reader it is the persona the unit serves, by
  name, and to read the card at the path the registry gives, whole, and speak from it; holds the
  criteria and the note verbatim; asks what the people the persona stands for meet when they
  upgrade, whether they could defend each sentence the plan states, and any work or spend they
  would not sign off; names no card section (0 matches for "Boundaries", "End Goals" and
  "Frustrations" in either), no seat card path and no review seat sentence; the qa and persona
  briefs each name the other seats on the panel as separate reviewers of the same note, without
  adopting them; and each footer names `critic.py approach record` with its own reviewer
  (`"Abena Osei (persona)"`, `"Sam Eriksson (qa)"`) and its own reply file at its round
- **Fails on:** HEAD, where `critic.py brief --seat persona` is refused with "brief refused: no
  seat card for 'persona' - neither the project nor the skill carries one (seats: engineering, qa,
  product)", and US1345's approach note refuses an unknown seat the same way (E6); HEAD plus
  US1344, where `approach brief` is an invalid choice (E5); and no brief generator reads a story's
  Persona field (E19)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_panel_brief.py::SolutionReviewPanelBriefTests::test_the_stakeholder_brief_frames_the_persona_and_no_seat
- **Verified:** yes (2026-11-28)

### AC3: a later round quotes that seat's own changes and no other seat's

- **Given** the same panel and story, a qa CHANGES at round 1 holding two numbered items, a product
  GO at round 1, no persona verdict, and the note revised; and the same story with the panel unset
  and a qa CHANGES recorded
- **When** `approach brief` is run for qa, product and persona under the panel, and for qa with the
  panel unset before and after its CHANGES is recorded
- **Then** qa's brief, at its round 2, quotes both of its own items as `>` lines and asks it to check
  each is answered in the note; product's and the persona's briefs quote no qa line; each still
  reads exactly one identity; and with the panel unset the two qa briefs are byte-equal, so US1345's
  brief is unchanged
- **Fails on:** HEAD plus US1344, where `approach brief` is an invalid choice (E5); and US1345's
  brief as its approach note composes it reads the unit, its criteria, the decisions and the note,
  and no ledger row (E6), so a round 2 brief carries none of the seat's changes
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_panel_brief.py::SolutionReviewPanelBriefTests::test_a_later_round_quotes_the_seat_s_own_changes
- **Verified:** yes (2026-11-28)

### AC4: a persona that cannot be framed is refused with a remedy, and a unit with none sits no stakeholder

- **Given** under the same panel: a story whose Persona is "Dani (Engineering)" (not in the
  registry); one whose Persona names a registry entry whose card file is missing; a project with no
  `sdlc-studio/personas/index.md`; the Abena Osei card with its Cast role changed to Secondary while
  the registry declares her Primary, under `personas.standard: block` and again under `report`; a
  3-point bug with no Persona field; and the Abena Osei story unchanged
- **When** `approach brief --seat persona` and `approach panel` are run for each
- **Then** for the unregistered name, the missing card and the missing registry both verbs exit 2
  with nothing on stdout, naming the name and `sdlc-studio/personas/index.md`, the missing card
  path, or the registry path and that `persona` on the panel needs it; under `block` both verbs
  exit 2 for the held card with nothing on stdout, naming the card, `persona-registry-role` and the
  `persona_review.py brief` command, so no roster names a brief that would be refused, and under
  `report` both print, each with one stderr warning naming the card; every
  persona refusal names a remedy: register the persona, correct the story's Persona field, or take
  `persona` off the panel; for the bug `approach brief --seat persona` exits 2 saying it names no
  Persona, and `approach panel` lists qa and product only, saying no stakeholder sits; and the
  unchanged Abena Osei story prints both (the control)
- **Fails on:** HEAD, where `critic.py brief --seat persona` is refused as an unknown seat with no
  word of the registry or the card (E6); HEAD plus US1344, where both verbs are invalid choices
  (E5). The fixture's held card is held at HEAD: `persona_review.blocking` returned
  `['persona-registry-role']` for it and `[]` for the unchanged card (E9)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_panel_brief.py::SolutionReviewPanelBriefTests::test_a_persona_that_cannot_be_framed_is_refused
- **Verified:** yes (2026-11-28)

### AC5: the code review stays independent of the panel, and the runbook and catalogue name it

- **Given** a 3-point story whose Persona is Maya Okafor, under the panel, with a recorded round:
  "Sam Eriksson (qa)" CHANGES with its reply file, "Lena Marsh (product)" GO and "Maya Okafor
  (persona)" GO; reference-sprint-toolchain.md's "Review a builder's approach" row; and
  reference-scripts-review.md's critic.py entry
- **When** `critic.py brief --unit <id> --seat qa`, `--seat product` and `--seat engineering` are
  run, the pages are read and `docgen.py surface --check` is run
- **Then** no code brief's stdout carries a reply file path, a line of the qa reply, the persona's
  name, or a GO or CHANGES word its capture before the record lacks; the qa and product briefs each
  print on stderr that the code reviewer must be a fresh context that has not read the note, and
  the engineering brief prints no such line, since the persona row makes no seat print it; the
  runbook row's command names `critic.py approach panel`, `critic.py approach brief` and `critic.py
  approach record`, with the table's three columns unchanged; the catalogue names the panel verb,
  the `--seat persona` form and the reply files, and says that with a panel set a round counts the
  reviewing seat's rows for the unit, and otherwise the unit's rows; and the surface check passes
- **Fails on:** HEAD plus US1344, where the qa and product code briefs after this round printed 0
  stderr lines naming a fresh context, an approach or a solution review (E8); under US1345 as its
  approach note plans the notice (`verdict_seat` of any row's reviewer, E16), "Maya Okafor
  (persona)" reads as engineering (E3), so the engineering brief would print it; and the catalogue
  has 0 matches for `approach panel`, `--seat persona` or `solution-review/`, and says only "the
  unit's rows so far plus one" (E17)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_panel_brief.py::SolutionReviewPanelBriefTests::test_the_code_review_stays_independent_and_the_runbook_names_the_panel
- **Verified:** yes (2026-11-28)

## Notes

- Depends on: S1 (test_one_identity_brief.py), S2 (critic.py; `effective_panel`, `panel_state`),
  US1345 (critic.py; `approach brief`, the code brief notice) and US1347 (reference-sprint-toolchain.md).
- Persona: Abena Osei, End goal 2: "Every specification and every change names an accountable
  person, not 'the agent'".
- Ran: the verb probes (E5), the persona seat refusal and US1345's note (E6), the code briefs after a
  panel round (E8), the registry and the standard (E9), the template card (E10), the seat readers
  (E3), the catalogue greps (E17).
- Size: this is the top of 3 points. If the builder's approach note will not fit, AC3 (C15) is the
  first part to move to a follow-up, as the product seat ruled.
- Add `approach brief --seat persona` (one identity, the persona) and `approach panel` (zero) to
  `test_one_identity_brief.GENERATORS`; S1's AC4 node then covers them.
- Intercept `--seat persona` before `persona_resolve.review_card`, which refuses it as an unknown
  seat (E6). Reuse US1345's criteria, decisions and note sections; the persona brief differs in its
  opening, its questions and its footer. Open with `You are <name>, ...` so S1's reader matches it.
- The held-card check reuses `persona_review.blocking`, `persona_review.refusal` (it names the card,
  each rule and a `Run next: ... persona_review.py brief --card ... --seat ...` line, E9) and
  `persona_review.standard_mode` (`block` when unset; the shipped default is `block`).
- AC3's quote reads the seat's own rows by `recorded_seat` and quotes its latest CHANGES cell as `>`
  lines; it quotes no other seat's reply. With the panel unset, leave US1345's brief, footer
  included, exactly as it is.
- The reply file's round is the seat's next round under S2's per-seat count.
- AC5's stderr check is a pin on the US1345 note: if US1345 lands keying its notice on
  `verdict_seat`, this story changes `solution_review_notice` to read `recorded_seat` first, falling
  back to `verdict_seat` only for a cell with no role.
- Repository data: open stories' Personas are all registered (product's probe); 21 old stories
  carry `Persona: Engineering seat`, 11 `Dani (Engineering)` and 8 `Sam Eriksson (QA)`, none
  registered, so a panel with `persona` refuses them loudly, as AC4 requires (E19).
- Readers beside the new module: reference-sprint-toolchain.md is read by 9 modules
  (test_lane_builder_brief.BuilderRunbookTests holds one table with columns Do, Command, Instead of;
  US1345's module holds the approach row; both kept); reference-scripts-surface.md by 17, holding it
  to `docgen.py surface --check`; reference-scripts-review.md by 2 (test_lean_config_keys_read,
  test_lean_docs_v64); `scripts/tests/retired_surface.py` refuses "plan review" and "two-role" in
  shipped text (E18).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-27 | engineering seat; product seat (D0648) | Groomed for run twenty-eight from the CR0757 breakdown: engineering draft with the product seat's six rulings and changes C1-C23 folded in |
