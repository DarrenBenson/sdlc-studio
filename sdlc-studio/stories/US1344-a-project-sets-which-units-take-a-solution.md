# US1344: A project sets which units take a solution review, and critic.py records a seat's go or changes against the approach note

> **Status:** Done
> **Risk-class:** high
> **Delivers:** CR0756
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_solution_review_record.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, changelog.d/US1344.md
> **Epic:** EP0385
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As** an engineering lead paying for every review round, **I want** to name which units take a
review of the builder's approach before code, and to have the verdict recorded against the note
it judged, **so that** a builder builds to an agreed plan and the record proves which plan.

## Acceptance Criteria

### AC1: the setting decides which units take the step

- **Given** a project setting `review.solution_review.min_points: 3` and
  `review.solution_review.risk_classes: [high]`, a 3-point standard story, a 2-point story whose
  risk class is high, a 2-point standard story, and a complete approach note for each
- **When** `critic.py approach record --unit <id> --verdict go --note <path> --reviewer
  "Dani (engineering)" --author "builder (engineering)"` is run for each
- **Then** the first two are recorded, each printing why it takes the step (3 points, at or above
  `review.solution_review.min_points` 3; risk class high, listed in
  `review.solution_review.risk_classes`), and the third is refused with exit 2, naming both
  settings and writing nothing. Fails on: HEAD, where `critic.py approach` is an invalid choice.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_record.py::SolutionReviewRecordTests::test_the_setting_decides_which_units_take_the_step
- **Verified:** yes (2026-11-28)

### AC2: a verdict is recorded against the note's digest, round by round

- **Given** the 3-point story and its note
- **When** `approach record --verdict changes --changes <file>` is run, the note is revised, and
  `approach record --verdict go` is run
- **Then** `sdlc-studio/reviews/solution-reviews.md` holds two rows for the story: CHANGES at
  round 1 with the first note's 12-hex sha256 digest and the changes text, then GO at round 2
  with the revised note's digest, each naming reviewer, author and date. Fails on: HEAD, which
  has no such verb and no such ledger.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_record.py::SolutionReviewRecordTests::test_a_verdict_is_bound_to_the_note_digest_round_by_round
- **Verified:** yes (2026-11-28)

### AC3: a verdict that cannot stand is refused

- **Given** the same story and note
- **When** `approach record` is run with a reviewer of the same identity as the author, with
  `--verdict go` and `--changes`, with `--verdict changes` and no changes, and with `--note`
  naming a missing file
- **Then** each exits 2 with its reason and leaves the ledger unchanged, while a well-formed
  record beside them exits 0 (the positive control). Fails on: HEAD, which has no such verb.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_record.py::SolutionReviewRecordTests::test_a_verdict_that_cannot_stand_is_refused
- **Verified:** yes (2026-11-28)

### AC4: the step ships off, and the reference says so

- **Given** a project that sets nothing
- **When** `config.py show --sources` is run, and reference-config.md is read
- **Then** it lists `default review.solution_review.min_points = 0` and `default
  review.solution_review.risk_classes = []`, `approach record` refuses every unit in it, the
  review table has a row for each key stating its default and that the step is off at it, the
  incremental-adoption sentence under Two-Backlog Enforcement names `review.solution_review`, and
  reference-config.md is no longer than 732 lines. Fails on: HEAD, where `config.py show --key
  review.solution_review.min_points` prints `no key` and exits 1.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_record.py::SolutionReviewRecordTests::test_the_step_ships_off_and_the_reference_says_so
- **Verified:** yes (2026-11-28)

## Notes

- Ran: the invalid-choice probe and the bare-project `config.py show` probes (Evidence S1).
- Read the keys with `config.get(root, "review.solution_review.min_points", 0)` and
  `config.get(root, "review.solution_review.risk_classes", [])`: `test_lean_config_code_defaults`
  holds every three-argument `config.get` default equal, in type and value, to the defaults
  file, and `test_lean_config_keys_read` holds every key read to a backticked row in
  reference-config.md and a declaration in the defaults.
- Keep the defaults comment free of an inline `a | b` mode list naming block or enforce, and of
  `#   word` lines above the keys: `test_lean_prd_refresh.gate_keys_off` would then count the key
  as a gate key shipped off, and hold prd.md's Feature Flags introduction to naming it.
- Do not add the ledger to sdlc-studio/trd.md's committed-records table in this story:
  `test_lean_trd_refresh.test_every_committed_record_is_listed` fails on a listed path git tracks
  no file for, unless it is also added to that test's `pending_records()`. Leave it, with the
  6.5 key lists in `test_lean_release_notes_v65.NEW_KEYS` and `test_lean_specs_v65.FLAGS`, to the
  release paperwork.
- Never call it "plan review" in any shipped text: `scripts/tests/retired_surface.py` refuses
  the phrase as retired.
- Expose `solution_review_reason(root, unit)` (None, or the reason) and
  `approach_agreed(root, unit, note)` (ok and why) for S3, S4 and S5 to call; do not change
  `critic.py show --format json`, whose `{unit, verdict}` shape other tests read.
- **Makes room on reference-config.md** (730 lines, ceiling 732, `check_budgets --drift` 4.58%
  over its 698 base): fold the severity-levels text block at lines 219-228 (read by no script
  and no test; `review.severity_levels` stays declared in the defaults) into one table row,
  saving 8 lines, then add the two rows: net minus 6. US1332, US1333 and US1336 also edit this
  page in run twenty-eight. Regenerate its reading guide with `docgen.py references` if it moves.
- Beside the existing tests: reference-config.md is read by 28 modules (among them
  test_config, test_lean_config_keys_read, test_lean_prd_refresh, test_check_budgets and the
  v6.5 release tests, which pin their own keys only); config-defaults.yaml by 38
  (test_config.ReviewKeysAreDeclaredTests scans only two-part `review.<leaf>` strings, so it does
  not see these keys); reference-scripts-review.md by test_lean_config_keys_read and
  test_lean_docs_v64; reference-scripts-surface.md by 17, which hold it to `docgen.py surface
  --check` and to naming no retired verb. None asserts anything these criteria contradict.
- Ruled in D0647: the step ships off (`min_points` 0, `risk_classes` []), so AC4 holds as written; this repository turns it on in US1347.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-26 | orchestrator (D0545) | Groomed: criteria with Fails on run at HEAD and Verify nodes, from the engineering seat's draft; default and this repository's setting per D0647 (product seat). |
| 2026-11-27 | orchestrator (D0545) | Affects gains `scripts/sprint_report.py` and its test: the new critic approach verb must be declared in `NON_CEREMONY_VERBS` (or given a checklist row), or `test_the_stage_set_and_the_cycle_cannot_drift_apart` refuses the commit |
