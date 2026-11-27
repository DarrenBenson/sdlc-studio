# US1349: The framing rules say a brief carries one identity, and a test holds every brief the skill prints to it

> **Status:** Ready
> **Risk-class:** elevated
> **Delivers:** CR0757
> **Created:** 2026-11-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-agent-prompt-template.md, .claude/skills/sdlc-studio/lessons/LL0057-give-every-subagent-a-persona-a-seated-agent-beats-a-generic-one.md, .claude/skills/sdlc-studio/reference-story.md, .claude/skills/sdlc-studio/reference-epic.md, .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/scripts/tests/test_one_identity_brief.py, changelog.d/US1349.md
> **Epic:** EP0386
> **Points:** 2
> **Depends on:** US1345
> **Persona:** Abena Osei

## User Story

As an engineering lead whose orchestrator delegates to subagents, I want every brief the skill prints, and every consultation it tells an orchestrator to run, to hand one agent exactly one identity, so that each reply is one named seat's or persona's judgement and no agent speaks for another.

## Acceptance Criteria

### AC1: the framing rules say one identity per brief

- **Given** reference-agent-prompt-template.md's framing list and LL0057
- **When** they are read
- **Then** the list opens "Five rules govern the framing"; the fifth rule's first sentence says a
  brief handed to an agent carries exactly one identity, one seat or one persona, never two; the
  rule says several views are several agents, one brief each, whose replies are recorded files the
  orchestrator passes on, and that no agent speaks for another; it says
  `scripts/tests/test_one_identity_brief.py` holds to it the lane, review, approach and seat briefs
  the skill prints; the rule's paragraph has 0 matches for "generator" and 0 for "every shipped";
  LL0057's How to apply states the rule and its Guard names that module in place of "None yet";
  and the page still has exactly one paragraph holding "fresh builder" and exactly one holding both
  "without subagents" and "lane run"
- **Fails on:** HEAD, where reference-agent-prompt-template.md line 145 reads "Four rules govern
  the framing, none negotiable:", the page has 0 matches for "one identity", and LL0057 line 18
  reads "**Guard.** None yet: CR0748 asks every brief the skill ships to name a seat and refuse one
  that does not." (E11)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_one_identity_brief.py::OneIdentityBriefTests::test_the_framing_rules_say_one_identity_per_brief

### AC2: story creation, epic creation and the amigo panel seat one agent per seat

- **Given** reference-story.md's step 9 ("Three Amigos Consultation (Default)"), reference-epic.md's
  step 7 ("Three Amigos + Stakeholder Assessment (Default)"), and a fixture project with this
  repository's three seat cards
- **When** the pages are read and `persona_resolve.py panel --ceremony refine --question "Is the
  panel fixed?"` is run
- **Then** reference-story.md's Process says each seat is its own agent: three agents in parallel,
  one per seat, each reviewing the stories the run generated, a seat getting more than one agent
  only when its stories will not fit in one; reference-epic.md's step 7 says each seat, and each
  stakeholder persona consulted, is its own agent with its own brief; no line of either step has
  one agent review from several perspectives; both steps still name `persona_resolve.py resolve
  --seat <product|engineering|qa> --render review`, that the seats ship with the skill and that the
  step needs no project user personas; reference-epic.md is at most 1,106 lines; and the panel's
  stdout keeps its first line, `refine amigo panel (Dani Okafor leads): ...`, and its next line says
  to brief one agent per seat with `persona_resolve.py resolve --seat <role> --render review` and
  take the questions to each
- **Fails on:** HEAD, where reference-story.md lines 191 and 192 read "Run consultations in
  parallel (one agent per epic)" and "Each agent reviews all stories in its epic from all three
  perspectives", reference-epic.md's step 7 (lines 111 to 137) has 0 lines naming an agent (E11),
  and the panel printed `take these 1 question(s) to the panel:` as its second line and no resolve
  command (E12)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_one_identity_brief.py::OneIdentityBriefTests::test_the_create_workflows_and_the_panel_seat_one_agent_per_seat

### AC3: a merged brief reads two identities, and a quoted one reads none

- **Given** a fixture story's lane brief; that brief with the first line of a qa `critic.py brief`
  appended; that brief with "You are Abena Osei, the persona this unit serves." appended, Abena Osei
  being in the fixture's persona registry; and that brief with "> You are the qa review seat."
  appended
- **When** the module's identity reader reads each
- **Then** it returns the engineering seat alone for the first, the engineering and qa seats for
  the second, the engineering seat and the Abena Osei persona for the third, and the engineering
  seat alone for the fourth; and the module's one-identity assertion fails on the second and third,
  naming both identities
- **Fails on:** HEAD, where no test reads or counts the identities a brief asks its reader to
  adopt: the modules that read an identity line (7 for the review seat sentence, 2 for the lane
  brief's seat line) assert it is present, never a count (E18); the prototype reader gave the
  lane brief plus a `>`-quoted qa sentence one identity, and the merged texts two (E13)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_one_identity_brief.py::OneIdentityBriefTests::test_a_merged_brief_reads_two_identities

### AC4: every brief the skill prints carries exactly one identity, and the panel none

- **Given** a fixture project with project seat cards for engineering, qa and product, a persona
  registry holding Abena Osei and Maya Okafor with their cards, a 3-point story whose Persona is
  Abena Osei, a complete approach note for it, a prior qa verdict file, and an open run
- **When** each row of the module's `GENERATORS` table is run: `sprint.py lane brief --units <id>`;
  `critic.py brief --unit <id> --seat <seat>` for each of the three seats; `critic.py brief --unit
  <id> --seat qa --rejoinder <file>`; `critic.py approach brief --unit <id> --seat <seat> --note
  <note>` for each of the three seats; `persona_resolve.py resolve --seat <seat>` at `--render
  build` and `--render review`; `persona_resolve.py resolve-consult --role <seat>`;
  `persona_resolve.py panel --ceremony refine --question X`; and `sprint.py goal-review brief --seat
  <seat>`
- **Then** each brief's stdout reads exactly one identity, the seat it was asked for, the rejoinder
  and the goal-review brief among them though the goal-review brief names both registered personas;
  and the panel's stdout reads zero
- **Fails on:** HEAD, where `critic.py approach` is an invalid choice, and HEAD plus US1344, where
  `approach brief` is (E5), so one generator cannot run; and no module runs any two generators side
  by side (E18)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_one_identity_brief.py::OneIdentityBriefTests::test_every_brief_the_skill_prints_carries_one_identity

## Notes

- Depends on: US1345 (its `approach brief` is a `GENERATORS` row). Shares no file with S2.
- Persona: Abena Osei, End goal 2: "Every specification and every change names an accountable
  person, not 'the agent'".
- Ran: the page lines (E11), the panel's output (E12), the identity reader over the lane brief, the
  rejoinder, the panel and a quoted sentence (E13), the reader counts (E18) and the generator
  timings (E19).
- The identity reader: a seat is `\bYou are the ([a-z][a-z0-9-]*) (?:review seat|amigo)\b` or
  `\badopt the (?:work|build|review) render of the ([a-z][a-z0-9-]*) seat card\b`; a persona is
  `You are <name>\b` for a name `sdlc_md.persona_registry(root)` holds, so the goal-review brief's
  "Abena Osei (Primary):" is a mention. A line whose first non-space character is `>` is quoted text
  and never counted. Write the patterns from the sentences as they stand when this is built; if
  US1345's opening sentence is none of these forms, add its form to the reader and never rewrite a
  generator to fit.
- Keep the generators as one table in the module (`GENERATORS`), each row naming its command and
  the identity count it must read; S3 and S4 add their rows to it.
- Run generators in-process where the module allows (`sprint.main`, `persona_resolve.main`), as
  test_lane_builder_brief does: as subprocesses a `critic.py brief` took 5.1 s, `lane brief` 8.4 s
  and `resolve` 2.9 s (E19).
- The approach note must be complete for US1345's brief to print (its five headings, and a Tests
  section naming every criterion id).
- The fifth rule must hold neither "fresh builder" nor both "without subagents" and "lane run":
  test_lane_brief_budget and test_lane_run count the paragraphs holding them and require 1 (E11).
- persona_resolve.py: change the text output of `panel` only, after its first line; leave
  `--format json` alone. test_lean_no_signoff_verbs line 174 asserts `"{ceremony} amigo panel"` in
  its stdout (E12).
- reference-epic.md step 7: reword the existing seating sentence and the "Consult affected
  stakeholder personas" bullet so the page gains no line (1,106 now, budget 1,102 inside its
  tolerance).
- The changelog fragment tells an upgrader three facts: story creation's Three Amigos step now runs
  one agent per seat where it ran one agent per epic covering all three, so each story is read by
  three agents; `--skip-personas` still skips the step; and epic creation's step says one agent per
  seat and per stakeholder, and `persona_resolve.py panel` now names the per-seat command.
- Readers beside the new module: reference-agent-prompt-template.md is read by 6 modules, none of
  which reads the framing list; reference-story.md by 4 (test_lean_create_path_reviews.AMIGO_DOCS
  holds the resolve command, "seats ship with the skill" and "no project user personas", all kept);
  reference-epic.md by 5 (test_lean_create_path_reviews; test_agent_definitions, the wave example;
  test_reconcile, step 4's Agentic mode; tools/tests/test_skill_metadata_neutral;
  test_check_budgets), none reading step 7 beyond AMIGO_DOCS' phrases; persona_resolve.py by 23,
  of which only test_lean_no_signoff_verbs reads the panel's text; LL0057 by none (lessons.py reads
  its index row, whose title does not change) (E18).
- Budgets: the template is 379 lines against the 600 reference budget; reference-story.md 1,081
  against 1,091; the step 9 fix replaces two lines (E17).
- US1325 (Draft, CR0748) also edits the template; it is not in this run.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-27 | engineering seat; product seat (D0648) | Groomed for run twenty-eight from the CR0757 breakdown: engineering draft with the product seat's six rulings and changes C1-C23 folded in |
