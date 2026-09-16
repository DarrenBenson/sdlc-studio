# HO-0071: Nothing is left open silently: the sixteen bugs open at planning (BG0659, BG0661, BG0662, BG0664-BG0676) reach Fixed on their own verifiers; a corpus-verify run dispatched on the commit BG0676 closes on - delivered last, carrying the whole batch - passes against a baseline measured in CI; and a run can no longer end silently over an unanswered unit or an unanswered REJECT - an unfinished batch unit holds the close through its stop-ship step and is named by every route that ends a run (D0193, D0196), a stop-ship ruling lives in the one table the close reads (D0194), and no story or bug reaches a delivered terminal over a REJECT whose findings were neither filed nor repaired, save by a recorded override

> **Date:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Run:** RUN-01M2JA6J (started 2026-09-15T10:41:35Z)
> **Outcome:** goal-reached
> **Goal:** done
> **Batch source:** run-state.json

## Where to pick up

6 of 23 unit(s) remain (0 suit copilot-assisted completion, 6 need human judgement). Plan them straight back in:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/sprint.py" plan \
  --worklist sdlc-studio/.local/handoff-worklist.txt --order wsjf
```

Each item below names the pointer to start from: the failing AC, the check it stalled at, the blocker that stopped it, or the file it was to touch.

## Unanswered stop-ship questions

None: every batch unit is delivered, abandoned, ruled, dropped, parked or awaiting only a signature. Rulings read from RETRO0117's `## Known issues carried` for RUN-01M2JA6J.

## Appetite

- **Declared:** wall-clock 5760 min, units 64 unit(s)
- **Spent:** 1569.6 min, 18 unit(s) terminal
- **Delivered:** 17 unit(s)
- **Token forecast:** ~5,764,577 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (17)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0659](../../sdlc-studio/bugs/BG0659-a-code-span-whose-value-ends-in-a.md) | bug | Fixed | 5/5 AC(s) verified; critic APPROVE (Dani Okafor (engineering seat, independent subagent, delivery)) |
| [BG0661](../../sdlc-studio/bugs/BG0661-revert-check-never-names-the-units-it-set.md) | bug | Fixed | 5/5 AC(s) verified; critic APPROVE (Dani Okafor (engineering seat, independent subagent, delivery)) |
| [BG0662](../../sdlc-studio/bugs/BG0662-nothing-checks-a-changelog-fragment-s-shape-until.md) | bug | Fixed | 5/5 AC(s) verified; critic APPROVE (Dani Okafor (engineering seat, independent subagent, delivery)) |
| [BG0664](../../sdlc-studio/bugs/BG0664-the-pre-push-boundary-gate-runs-no-boundary.md) | bug | Fixed | 3/3 AC(s) verified; critic APPROVE (Dani Okafor (engineering seat, independent subagent, delivery)) |
| [BG0665](../../sdlc-studio/bugs/BG0665-seven-of-thirteen-review-settings-are-absent-from.md) | bug | Fixed | 3/3 AC(s) verified; critic APPROVE (Dani Okafor (engineering seat, independent subagent, delivery)) |
| [BG0666](../../sdlc-studio/bugs/BG0666-an-unauthored-test-plan-row-is-exempt-from.md) | bug | Fixed | 3/3 AC(s) verified; critic APPROVE (Dani Okafor (engineering seat, independent subagent, delivery)) |
| [BG0668](../../sdlc-studio/bugs/BG0668-tag-check-refuses-on-a-close-the-close.md) | bug | Fixed | 3/3 AC(s) verified; critic APPROVE (Sam Eriksson (qa seat, independent subagent, delivery)) |
| [BG0669](../../sdlc-studio/bugs/BG0669-conformance-demands-acceptance-criteria-of-a-story-retired.md) | bug | Fixed | 7/7 AC(s) verified; critic APPROVE (Dani Okafor (engineering seat, independent subagent, delivery)) |
| [BG0670](../../sdlc-studio/bugs/BG0670-config-py-show-crashes-on-a-config-holding.md) | bug | Fixed | 3/3 AC(s) verified; critic APPROVE (Sam Eriksson (qa seat, independent subagent, delivery)) |
| [BG0671](../../sdlc-studio/bugs/BG0671-critic-py-s-brief-practice-and-claim-pass.md) | bug | Fixed | 5/5 AC(s) verified; critic APPROVE (Dani Okafor (engineering seat, independent subagent, delivery)) |
| [BG0672](../../sdlc-studio/bugs/BG0672-critic-record-accepts-a-brief-fingerprint-no-brief.md) | bug | Fixed | 5/5 AC(s) verified; critic APPROVE (Dani Okafor (engineering seat, independent subagent, delivery)) |
| [BG0673](../../sdlc-studio/bugs/BG0673-the-repair-plan-gate-ep0106-is-wired-into.md) | bug | Fixed | 7/7 AC(s) verified; critic APPROVE (Dani Okafor (engineering seat, independent subagent, delivery)) |
| [BG0674](../../sdlc-studio/bugs/BG0674-sprint-next-materialises-a-charter-s-discovery-items.md) | bug | Fixed | 4/4 AC(s) verified; critic APPROVE (Dani Okafor (engineering seat, independent subagent, delivery)) |
| [BG0675](../../sdlc-studio/bugs/BG0675-an-author-declared-points-value-sets-a-unit.md) | bug | Fixed | 4/4 AC(s) verified; critic APPROVE (Dani Okafor (engineering seat, independent subagent, delivery)) |
| [BG0676](../../sdlc-studio/bugs/BG0676-the-scheduled-corpus-verify-lane-is-red-on.md) | bug | Fixed | critic REJECT (Dani Okafor (engineering seat, independent subagent, delivery, round 1)) |
| [BG0677](../../sdlc-studio/bugs/BG0677-critic-py-repair-cannot-close-a-finding-whose.md) | bug | Fixed | 7/7 AC(s) verified; critic APPROVE (Dani Okafor (engineering seat, independent subagent, delivery)) |
| [BG0678](../../sdlc-studio/bugs/BG0678-a-wired-repair-plan-gate-keeps-no-rounds.md) | bug | Fixed | 6/6 AC(s) verified; critic APPROVE (Dani Okafor (engineering seat, independent subagent, delivery)) |

## Remaining (6)

### BG0667 (bug, Fixed) - judgement

- **check:** `verify:unproven` - the file says delivered; the evidence says 1 red AC(s) - reconcile the two (re-run verify_ac, fix, or reopen)
- **ac:** `AC4` - pytest .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py::RealTreeMarkerTests::test_the_control_is_green_in_either_fragment_state (pytest)
- **issue:** `missing-regression-test` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0667-the-root-effect-control-s-real-tree-marker.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by verify:unproven, difficulty:low

### US0625 (story, Review) - judgement

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::StopShipRulingTests::test_the_doctrine_states_the_per_finding_rule (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::StopShipRulingTests::test_a_finding_with_no_ruling_is_refused (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::StopShipRulingTests::test_two_findings_keep_their_own_rulings (pytest)
- **file:** `.claude/skills/sdlc-studio/reference-doctrine.md` - declared Affects
- **file:** `tools/tests/test_doctrine_stop_ship.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/retro.py` - declared Affects
- **file:** `sdlc-studio/stories/US0625-the-doctrine-states-cr0526-s-rule-names-the.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high

### US0627 (story, Review) - judgement

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_recorded_reject_blocks_done (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_filed_artefact_id_discharges_the_reject (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_stop_ship_ruling_discharges_the_reject (pytest)
- **ac:** `AC4` - pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_an_id_naming_no_artefact_is_refused (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/transition.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_transition.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0627-a-story-or-bug-reaching-done-or-fixed.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:extreme

### US0626 (story, Review) - judgement

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseRefusesNonTerminalTests::test_close_refuses_and_names_the_unit (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseRefusesNonTerminalTests::test_stop_refuses_on_the_same_condition (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseRefusesNonTerminalTests::test_the_refusal_names_where_the_findings_went (pytest)
- **ac:** `AC4` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseRefusesNonTerminalTests::test_a_terminal_batch_still_closes (pytest)
- **issue:** `unmet-deps: US0625:Review, US0627:Review` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py` - declared Affects
- **file:** `sdlc-studio/stories/US0626-an-unfinished-batch-unit-holds-the-close-through.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:extreme, issue:unmet-deps

### US0628 (story, Review) - judgement

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ClosedOverRejectNamesTheBugTests::test_the_story_names_the_filed_artefact (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ClosedOverRejectNamesTheBugTests::test_a_ruling_is_named_with_its_author (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ClosedOverRejectNamesTheBugTests::test_an_ordinary_close_writes_no_discharge_line (pytest)
- **issue:** `unmet-deps: US0627:Review` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/transition.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_transition.py` - declared Affects
- **file:** `sdlc-studio/stories/US0628-a-unit-closed-over-a-reject-names-in.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:unmet-deps

### US0823 (story, Review) - judgement

- **issue:** `unmet-deps: US0626:Review` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/handoff.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/help/handoff.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/help/sprint.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-sprint.md` - declared Affects
- **file:** `sdlc-studio/stories/US0823-every-other-route-that-ends-a-run-reads.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:unmet-deps

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Generated at the run close (`handoff generate`) |
