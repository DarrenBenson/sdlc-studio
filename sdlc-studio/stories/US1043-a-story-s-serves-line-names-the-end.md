# US1043: A story's Serves line names the End goal it serves, and validate serves checks it is on the card

> **Status:** Draft
> **Delivers:** CR0623
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/persona_goals.py, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/templates/core/story.md, .claude/skills/sdlc-studio/reference-story-sections.md, .claude/skills/sdlc-studio/reference-persona.md, .claude/skills/sdlc-studio/reference-scripts-verify.md, .claude/skills/sdlc-studio/scripts/tests/test_serves_goal_reference.py, changelog.d/US1043.md
> **Epic:** EP0285
> **Points:** 3
> **Depends on:** US1039
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, reading stories her agent wrote
**I want** each story to say which End goal of which persona it serves, in a form the tooling checks, instead of a persona summary copied into every story
**So that** the seats read a real trace to a goal rather than a block they have learned to skip

## Acceptance Criteria

- **AC1:** Given a story tagged `> **Serves:** Maya Okafor #2` and Maya's card listing End goal 2, when `validate.py serves` runs, then the tag resolves with no warning and the coverage output counts Maya's End goal 2 as served.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_serves_goal_reference.py::ServesGoalTests::test_goal_reference_resolves_and_counts
- **AC2:** Given a story tagged `Maya Okafor #9` while Maya's card lists four End goals, when `validate.py serves` runs, then it warns `serves-goal-unresolved` naming the story, the persona and the End goal numbers the card does have.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_serves_goal_reference.py::ServesGoalTests::test_goal_number_not_on_the_card_warns
- **AC3:** Given the PRD, a Draft story and a Done story each tagged with a persona and no End goal number, when `validate.py serves` runs, then it warns `serves-no-goal` for the Draft story only.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_serves_goal_reference.py::ServesGoalTests::test_no_goal_warns_on_open_stories_only
- **AC4:** Given `templates/core/story.md` and the Serves example `reference-story-sections.md` documents, when the test reads both, mints a story with `artifact.py new --type story --template full`, and runs `validate.py serves` on a fixture story carrying the documented example, then neither the template nor the minted story has a `### Persona Reference` section and the fixture draws no warning.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_serves_goal_reference.py::StoryTemplateTests::test_template_and_full_mint_drop_persona_reference_and_documented_serves_validates

## Notes

- Release: 6.2 (D0355 breakdown G11, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the resolver keeps reading `Maya Okafor #2` as a persona name and warns `serves-unresolved` (today's behaviour), or drops the goal number from coverage
- AC2 must fail on: the number is parsed but never checked against the card
- AC3 must fail on: the rule fires on the PRD, or on a delivered story, so adopting the template flags a whole delivered backlog
- AC4 must fail on: the template keeps the block, the full-template renderer keeps its own copy of it, or the docs show a Serves form the parser rejects (LL0040: the mint, not only the file)
- Serves: Maya Okafor #4.
- Grammar: `<Persona name> #<n>` per comma-separated entry, n numbered as on the card (panel, Q2: numbers for 6.2; the goal-review brief and the product seat's scenario already cite them; renumbering is a card change RFC0061's review on change (D7) would catch). Parsed and resolved in lib/persona_goals.py, so validate, the --serves writer and review prep read one grammar.
- Takes the CR's 'drop it' branch. The `> **Persona:**` and `> **Serves:**` header lines (templates/core/story.md:11-12) carry who and which goal, and the `### Persona Reference` block (story.md:33) goes. Corrected fact: the default and `--template planning` mints never render the block, but `--template full` grafts it from templates/core/story.md with its placeholders unfilled, so dropping it from the template also drops it from that mint. None of the three writes the `Serves:` header, which is why the --serves writer story exists.
- `serves-no-goal` applies to stories, not prd.md, and skips delivered terminals (`sdlc_md.is_delivered_terminal`, sdlc_md.py:1660) and terminal decisions (panel, Q7).
- Adds `serves-goal-unresolved` and `serves-no-goal` to the reference-persona.md rule table.
- Existing stories keep their block; no rule is added against it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G11 after the refine panel's review |
