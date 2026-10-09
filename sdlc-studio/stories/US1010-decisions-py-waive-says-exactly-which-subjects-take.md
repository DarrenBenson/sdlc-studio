# US1010: decisions.py waive says exactly which subjects take a scope tail and what an unscoped waiver covers, and refuses a tail nothing reads

> **Status:** Draft
> **Delivers:** CR0614
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/engagement_floor.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/help/decisions.md, .claude/skills/sdlc-studio/reference-scripts-create.md, .claude/skills/sdlc-studio/scripts/tests/test_waive_scope_help.py, changelog.d/US1010.md
> **Epic:** EP0279
> **Points:** 3
> **Depends on:** US1007, US1009, BG0997
> **Persona:** Maya Okafor

## User Story

**As** a team lead recording a waiver from the command's own help
**I want** the help and the output to state what a waiver will cover, and the command to refuse a scope nothing reads
**So that** a waiver my team records does what the help says, or is refused, and is never recorded and inert

## Acceptance Criteria

- **AC1:** Given `decisions.py waive --help`, when the test composes the expected --subject text from the tail grammar each checker publishes, then the help names each family's tail and says a leg waiver takes none, and every family the help names publishes a grammar.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_waive_scope_help.py::WaiveScopeHelpTests::test_the_subject_help_matches_each_checkers_published_tail
- **AC2:** Given the subject `leg:tsd:US0001`, when `decisions.py waive` runs, then it exits 2 saying a leg waiver takes no scope, and writes nothing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_waive_scope_help.py::WaiveScopeHelpTests::test_a_scope_on_a_leg_waiver_is_refused
- **AC3:** Given the subject `rule:engagement-floor:not-a-unit`, when `decisions.py waive` runs, then it exits 2 naming the unit-id form, and writes nothing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_waive_scope_help.py::WaiveScopeHelpTests::test_an_engagement_floor_tail_must_name_a_unit
- **AC4:** Given the subject `rule:conformance:critiqued:US-01JQK3F8`, when `decisions.py waive` runs, then it records the waiver, because conformance's lookup already matches that unit.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_waive_scope_help.py::WaiveScopeHelpTests::test_a_dashed_v3_unit_is_a_valid_conformance_scope
- **AC5:** Given the unscoped subject `rule:sprint-checklist:goal-judged`, when `decisions.py waive` records it, then its output says the waiver answers that row on every run whose checklist is read, earlier runs included, and names the run-scoped form.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_waive_scope_help.py::WaiveScopeHelpTests::test_an_unscoped_checklist_waiver_says_what_it_covers

## Notes

- Release: 6.2 (D0355 breakdown G5, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the help keeps today's sentence, 'an optional `:<unit>`/`:<id>-<id>` tail scopes it', which is true of conformance alone.
- AC2 must fail on: `subject_error`'s colon-boundary rule admits any tail on a declared subject, which records this today and covers nothing (review_prep reads `leg:tsd` exactly).
- AC3 must fail on: the engagement-floor family has no tail check, so a non-id tail records clean and the floor's exact-id lookup never finds it.
- AC4 must fail on: `conformance.scope_tail_error` keeps testing `sdlc_md.id_number`, which returns None for a ULID id, so the record-time check refuses what the lookup would honour.
- AC5 must fail on: the unscoped path prints only the existing `waived ... -> Dxxxx` line.
- The help is a literal (panel change 6). Composing it through `waivable_subjects` at parser build would put the AST scan on every `decisions.py` call, measured by the panel at 2.3 to 2.5 s warm against 0.66 s for `list` today. AC1's test composes the expected text from each checker's published grammar and compares both ways, so the derivation LL0042 asks for lives in the test.
- Each checker publishes its tail grammar beside its `scope_tail_error`. sprint_report and conformance already have one; engagement_floor gains one. A family whose checker publishes no grammar takes no tail, which is the rule AC2 applies to `leg:`.
- The conformance fix mirrors `_scope_covers`: try the single-id reading through `sdlc_md.norm_id` before the range reading, because a ULID id carries the same dash a range does. The panel keeps it here because this story is in 6.2; if the story slips, file it as a bug so it is not lost.
- AC3's positive case (`rule:engagement-floor:BG-01JQK3F8` records) already passes today. Whether that waiver covers its unit is BG0997's criterion. This story orders after BG0997 for the shared matcher only.
- The unscoped warning moved here from US-1, reworded per the panel: an unscoped waiver answers every run whose checklist is read, not only later ones.
- Corrects the comment at decisions.py:175, which says the scan 'costs about a third of a second', to the measured 2.3 to 2.5 s.
- reference-scripts-create.md (:174-178) documents `waive` and `waiver_for`'s matching rule. US-3 and this story both change them.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G5 after the refine panel's review |
