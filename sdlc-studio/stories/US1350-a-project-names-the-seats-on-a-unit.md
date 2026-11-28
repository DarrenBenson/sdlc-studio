# US1350: A project names the seats on a unit's approach panel, each records its own verdict in its own rounds, and the approach is agreed only when every one has a GO

> **Status:** Done
> **Risk-class:** high
> **Delivers:** CR0757
> **Created:** 2026-11-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_solution_review_panel.py, changelog.d/US1350.md
> **Epic:** EP0386
> **Points:** 3
> **Depends on:** US1344, US1345
> **Persona:** Abena Osei

## User Story

As an engineering lead, I want to name which seats review a builder's approach, each recording its own verdict, so that the product seat and the stakeholder see the plan before code and no seat's GO stands in for another's.

## Acceptance Criteria

### AC1: a set panel names who may record, and an unset one records as before

- **Given** `review.solution_review.min_points: 3` and `review.solution_review.panel: [qa, product,
  persona]`, a 3-point story built by the engineering seat whose Persona is Abena Osei, a registry
  holding Abena Osei and Maya Okafor, and a note
- **When** `critic.py approach record --verdict go` is run with reviewers "Sam Eriksson (qa)",
  "Lena Marsh (product)" and "Abena Osei (persona)"; then with "Ola Ade (engineering)", "Sam
  Eriksson" and "Maya Okafor (persona)"; then once with the panel set to `[qa, nobody]`; and, with
  the panel unset, with "Ola Ade (engineering)"
- **Then** the first three are recorded; "Ola Ade (engineering)" is refused naming the panel's
  seats, "Sam Eriksson" for naming no `(<seat>)`, and "Maya Okafor (persona)" naming the story's
  Persona, Abena Osei; `[qa, nobody]` is refused naming `review.solution_review.panel` and what it
  may hold (a seat the project has a card for, or `persona`); each refusal exits 2 with the ledger
  byte-equal; and with the panel unset "Ola Ade (engineering)" is recorded as US1344 records it
- **Fails on:** HEAD plus US1344, where with no project setting `config.py show --key
  review.solution_review.panel` printed "config: no key `review.solution_review.panel` - neither
  config-defaults.yaml nor the project's .config.yaml declares it" and exited 1 (E4); and with the
  panel set in the project config, "Ola Ade (engineering)", "Sam Eriksson" and "Maya Okafor
  (persona)" were each recorded against one note, exit 0, at rounds 4, 5 and 6 (E2)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_panel.py::SolutionReviewPanelTests::test_the_panel_names_who_may_record
- **Verified:** yes (2026-11-28)

### AC2: with a panel set each seat numbers its own rounds, and unset the unit's rows number them

- **Given** the same panel, story and note; and a second fixture with the panel unset
- **When** under the panel qa records CHANGES, product GO and Abena Osei (persona) GO against the
  note, the note is revised, and qa records GO; and with the panel unset qa records CHANGES and
  product GO on one note
- **Then** under the panel the ledger's four rows read rounds 1, 1, 1 and 2, the last being qa's
  second, each Reviewer cell naming its seat; and with the panel unset the two rows read rounds 1
  and 2, as US1344 numbers them
- **Fails on:** HEAD plus US1344, which numbers a unit's rows across seats whatever the project
  sets: qa CHANGES, product GO and Abena Osei (persona) GO on one note were recorded at rounds 1, 2
  and 3 (E1), and under a set panel the next three records took rounds 4, 5 and 6 (E2). The unset
  control holds there now (rounds 1 and 2, E1) and must still hold
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_panel.py::SolutionReviewPanelTests::test_each_seat_numbers_its_own_rounds
- **Verified:** yes (2026-11-28)

### AC3: the approach is agreed only when every seat on the unit's panel has a GO on the note as it stands

- **Given** the same panel: first, qa CHANGES then product GO on one note; then AC2's rows; then
  product and persona GO on the revised note; a 3-point bug with no Persona field and qa and product
  GO on its note; the engineering-built story under `[qa, engineering]` with a qa GO; and the bug
  under `[engineering]`
- **When** `critic.approach_agreed(root, unit, note)` and `critic.effective_panel(root, unit)` are
  called after each, and under `[engineering]` `approach record` is run with "Sam Eriksson (qa)"
- **Then** the first is not agreed, naming qa's CHANGES at round 1; the second is not agreed,
  naming product's and the persona's GO digests beside the note's digest now; the third is agreed,
  its reason naming each seat's round and the one digest; the bug is agreed on qa and product
  alone, its reason saying it names no Persona, so no stakeholder sits; under `[qa, engineering]`
  the effective panel is `[qa]`, engineering skipped because it builds the unit, the qa GO agrees,
  and the agreed reason says engineering was skipped and why; and under `[engineering]` the record
  is refused, exit 2, naming the panel and the building seat, with the ledger byte-equal; and with
  the panel unset `approach_agreed`'s messages are byte for byte US1344's
- **Fails on:** HEAD plus US1344, where `approach_agreed` reads the unit's last row only: after qa's
  CHANGES then product's and the persona's GO on one note it returned `(True, 'GO at round 3
  against note digest 575ed7e198c5')` (E1); and under `[engineering]` a qa GO on the bug was
  recorded at round 1 and `approach_agreed` returned `(True, 'GO at round 1 against note digest
  575ed7e198c5')` (E2)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_panel.py::SolutionReviewPanelTests::test_the_approach_is_agreed_only_when_every_seat_has_a_go
- **Verified:** yes (2026-11-28)

### AC4: the config reference says what the panel does

- **Given** a bare project and reference-config.md
- **When** `config.py show --sources` is run and the page is read
- **Then** it lists `default review.solution_review.panel = []`; the review table has a row for the
  key saying three things: empty means one seat's GO agrees the approach; a list names the seats,
  each its own agent and its own review, so each seat on the panel adds one review a round; and
  `persona` sits only for a unit that names a Persona, and the seat that builds a unit is skipped
  for that unit; the row has 0 matches for "as before" and 1 each for "its own review" and
  "skipped"; and reference-config.md is at most 732 lines
- **Fails on:** HEAD plus US1344, where `show --sources` on a bare project prints 0 lines naming
  `review.solution_review.panel` (E4), and reference-config.md and config-defaults.yaml have 0
  matches for `solution_review.panel` (E17)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_panel.py::SolutionReviewPanelTests::test_the_reference_says_what_the_panel_does
- **Verified:** yes (2026-11-28)

## Notes

- Depends on: US1344 and US1345 (critic.py). Shares no file with S1, US1347 or US1348.
- Persona: Abena Osei, End goal 1: "Every release passes the change board on the evidence the run
  produced, with no separate write-up".
- Ran: the unset-panel rounds and agreement (E1), the records under a set panel and under
  `[engineering]` (E2), the seat readers (E3), the config probes (E4), the reference greps (E17).
- Key a row's seat on `critic.recorded_seat` (the `(<role>)` group), never `seat_for` or
  `verdict_seat`: in this repository both read "Maya Okafor (persona)" as engineering, because the
  engineering card's holder is Dani Okafor (E3). Pin it: a panel `[qa, persona]` for a story whose
  Persona is Maya Okafor is agreed on GOs from qa and "Maya Okafor (persona)".
- The building seat is `run_state.lane_seat(root, unit) or critic.BUILD_SEAT`. Skipping it, rather
  than refusing the panel, lets one project setting serve units built by different seats.
- Expose `effective_panel(root, unit) -> (seats, skipped)`, `skipped` mapping each left-out entry to
  why (it builds the unit; the unit names no Persona), and `panel_state(root, unit, note=None)` (each
  seat's latest row, the skipped seats, agreed and why; with no note, agreed means every seat's GO
  shares one digest) for S3 and S4. Keep `approach_agreed`'s signature, and its messages for an
  unset panel byte for byte: US1347's land refusals quote them.
- Validate the setting where `solution_review_settings` does, refusing a wrong shape rather than
  reading it as empty. `persona` is reserved: refuse the setting when a project seat card declares
  the role `persona`.
- Defaults comment: no inline `a | b` list naming block or enforce, and no `#   word` lines above the
  key (test_lean_prd_refresh.gate_keys_off), as US1344 does for its keys.
- Between S2's land and S3's, the catalogue still says a round is "the unit's rows so far plus
  one", which stays true for an unset panel; S3 adds the panel clause (C19).
- Readers beside the new module: critic.py is read by 221 modules, among them US1344's
  test_solution_review_record (one reviewer per unit, so with the panel unset its rounds are
  untouched) and the EP0385 modules being built (each records one seat per unit with no panel set);
  config-defaults.yaml by 38 (test_lean_config_code_defaults holds the three-argument default equal
  to the file); reference-config.md by 29 (test_lean_config_keys_read needs a backticked row for the
  key) (E18).
- Budget: reference-config.md is 724 lines at HEAD plus US1344 against a hard limit of 732; one row
  brings it to 725; regenerate its reading guide with `docgen.py references` if spans move (E17).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-27 | engineering seat; product seat (D0648) | Groomed for run twenty-eight from the CR0757 breakdown: engineering draft with the product seat's six rulings and changes C1-C23 folded in |
