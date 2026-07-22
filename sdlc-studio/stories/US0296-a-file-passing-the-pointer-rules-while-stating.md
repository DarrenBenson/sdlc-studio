# US0296: A file passing the pointer rules while stating no working model is reported with what is missing

> **Status:** Review
> **Delivers:** CR0353
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py,.claude/skills/sdlc-studio/templates/agent-instructions.md
> **Epic:** EP0097
> **Points:** 3

## User Story

**As a** maintainer repairing an AGENTS.md the check has just failed
**I want** each working-model finding to name the missing element and the template section that
supplies it
**So that** I can fix the file from the report alone, and the report can no longer call a file good
when it establishes nothing about how the project is developed

## Context

This story supplies the discriminating fixture and the actionable message for the rules US0295
adds. The fixture is the proof obligation: an AGENTS.md that satisfies all six existing rules while
stating no working model must pass the six and fail the new ones. If it passes both sets, the new
rules restate the pointers and are worthless.

The template is in scope because the messages cite it. The four elements currently live in prose
under "Non-negotiable gates" and "How to work" item 5 of
`templates/agent-instructions.md`; a message can only cite an anchor the template actually carries,
so any heading the citation needs is added here.

`cmd_instructions` prints "agent-instructions files look good." when the violation list is empty.
That line is the false assurance CR0353 was raised about, and the fixture must not be able to
produce it.

## Acceptance Criteria

### AC1: the pointer-perfect fixture fails the working-model rules

- **Given** a fixture AGENTS.md that satisfies all six existing rules (present file, thin CLAUDE.md
  pointer, doctrine pointer, LATEST.md pointer, release gate, compaction re-read) and states no
  working model
- **When** `check_instructions` runs
- **Then** none of the six existing rules fires and one finding is returned per missing
  working-model element, so the fixture proves the new rules discriminate rather than restating the
  six
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_validate.py -k test_pointer_perfect_fixture_fails_only_the_working_model_rules
- **Verified:** yes (2026-07-22)

### AC2: every working-model finding names its element and its template section

- **Given** the findings returned for that fixture
- **When** each message is read
- **Then** it names the specific missing element and cites the section of
  `templates/agent-instructions.md` that supplies it, so the repair needs no read of the whole
  template
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_validate.py -k test_each_working_model_finding_cites_a_template_section
- **Verified:** yes (2026-07-22)

### AC3: a cited section that does not exist fails the suite

- **Given** the section names the messages cite
- **When** the suite runs
- **Then** each cited name is matched against the headings of the shipped
  `templates/agent-instructions.md`, so renaming or removing a section in the template fails the
  test rather than leaving the messages pointing at nothing
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_validate.py -k test_cited_template_sections_exist_in_the_shipped_template
- **Verified:** yes (2026-07-22)

### AC4: the report stops calling such a file good

- **Given** the same fixture as the project root
- **When** `validate instructions` runs over it
- **Then** the output lists the working-model findings and does not print "agent-instructions files
  look good."
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_validate.py -k test_report_never_calls_a_working_model_less_file_good
- **Verified:** yes (2026-07-22)

## Open Questions

- [x] Settled in the build: each finding cites a top-level heading AND a literal anchor line from
  that section (`template_section` + `template_anchor`), so the citation is precise without adding
  headings the template does not want. Both are matched against the shipped template by
  `test_cited_template_sections_exist_in_the_shipped_template`, so renaming either fails the
  suite. The only template change is the independent-review statement, which the template did not
  previously carry at all.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Groomed: user story + 4 executable ACs (discriminating fixture, actionable messages, citation guard, report honesty); Affects path corrected to templates/agent-instructions.md |
| 2026-07-22 | sdlc-studio | Built: TDD, mutation-tested; open questions closed |
