# US0295: check_instructions verifies the working model is stated, not only that cross-references exist

> **Status:** Draft
> **Delivers:** CR0353
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py
> **Epic:** EP0097
> **Points:** 5

## User Story

**As an** operator who trusts the hygiene check to say the instructions file is sound
**I want** the check to test that the file states how the project is actually developed, not only
that it cross-references four other documents
**So that** a clean report means the working model survived, rather than meaning four pointers are
present in a file that never says work is done this way

## Context

`check_instructions` applies six rules today: AGENTS.md exists, CLAUDE.md imports `@AGENTS.md`, and
the text mentions the operating doctrine, LATEST.md, a release gate and the compaction re-read.
Every one is a cross-reference; none asserts a practice. The shipped
`templates/agent-instructions.md` does carry the working model (delivery through the skill's chain
under "Non-negotiable gates", the deterministic-tooling rules and the executable-AC gate under
"How to work" item 5), so the exemplar is the bar the new rules must clear.

The four elements CR0353 names, each becoming its own rule so a finding is specific:

1. delivery flows through stories and sprints rather than ad-hoc coding
2. ids and index rows are tool-allocated, never hand-authored
3. a story reaches Done only when its executable ACs pass
4. review is independent of the author

Keep the new rules `warning` severity, matching the existing content rules: only `no-agents` is an
error, and this story does not change the exit contract.

## Acceptance Criteria

### AC1: each working-model element has its own rule and fires by name

- **Given** an AGENTS.md that carries every existing pointer but states no working model
- **When** `check_instructions` runs
- **Then** it returns one distinct rule id per missing element - delivery through stories and
  sprints, tool-allocated ids and index rows, executable ACs gating Done, and independent review -
  so a caller can tell which practice is absent without reading the file
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_validate.py -k test_working_model_rules_fire_per_missing_element
- **Verified:** yes (2026-07-22)

### AC2: the shipped template satisfies every new rule

- **Given** `templates/agent-instructions.md` with its guidance comment stripped, saved as a
  project's AGENTS.md
- **When** `check_instructions` runs
- **Then** it returns no working-model finding, proving the exemplar the check tells people to copy
  passes the bar the check sets
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_validate.py -k test_shipped_template_satisfies_the_working_model_rules
- **Verified:** yes (2026-07-22)

### AC3: a recorded opt-out is reported as an opt-out, not as a defect

- **Given** a project that has recorded a deliberate opt-out for one of the four practices
- **When** `check_instructions` runs
- **Then** that element is reported as opted out under its own rule id and severity, is not counted
  among the missing-element defects, and the other three rules still apply unchanged
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_validate.py -k test_a_recorded_opt_out_is_reported_as_such
- **Verified:** yes (2026-07-22)

## Open Questions

- [x] Ruled by D0052: a `.config.yaml` key, `instructions.working_model_opt_out`, READ BY CODE
  (`validate.working_model_opt_outs`), with a test proving the key changes behaviour. Built that
  way; a mutant that stops reading the key is killed by
  `test_a_recorded_opt_out_is_reported_as_such`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Groomed: user story + 3 executable ACs (per-element rules, template-satisfies-its-own-bar, opt-out honesty); opt-out surface left open |
| 2026-07-22 | sdlc-studio | Built: TDD, mutation-tested; open questions closed |
