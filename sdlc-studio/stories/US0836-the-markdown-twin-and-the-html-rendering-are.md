# US0836: the Markdown twin and the HTML rendering are generated from the shipped templates, and a section with no data renders NOT MEASURED by name

> **Status:** Draft
> **Delivers:** RFC0059
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/templates/reports/sprint-report.html
> **Epic:** EP0255
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** the Markdown twin and the HTML rendering are generated from the shipped templates, and a section with no data renders NOT MEASURED by name
**So that** RFC0059 is delivered by work that can be planned and checked

## Acceptance Criteria

Both shipped templates were derived from a worked prototype built over RUN-01M2JA6J's own
artefacts, which is what makes their shape trustworthy and their CONTENT a trap: the HTML still
carries that run's facts in prose no placeholder covers - forge run id 35085712929, the
4,271,975 opening meter reading, `Sam Eriksson`, `Dani Okafor`, a sprint goal quoted in full, a
13% rework rate - sitting beside the tokens that will be substituted. A renderer that fills the
double-brace tokens and emits the surrounding sentences verbatim therefore ships another run's
facts as this one's, and every assertion about substitution still passes. That is the defect
these criteria are written against.

D2a is settled and AC3 holds it: the JSON is of record, the Markdown twin is committed, and the
HTML is generated on demand and never written into the tree. THE RENDERED RUN is US0835's
fixture report, built for a run whose id, verified sha, retro id, reviewers, personas and every
figure share no value with RUN-01M2JA6J.

### AC1: no unsubstituted token and no prototype literal survives a render

- **Given** THE RENDERED RUN
- **When** `sprint_report.py render --report <the report id> --format md` runs, and again with `--format html`
- **Then** neither output contains an unsubstituted template token in the double-brace form the templates use; and neither contains `RUN-01M2JA6J`, `35085712929`, `4,271,975`, `Sam Eriksson` or `Dani Okafor`, none of which the fixture supplies - so any sentence carrying a prototype fact fails this criterion whether or not it sits next to a token
- **Mutant:** substitute the tokens and emit the template's prose unchanged around them - every figure is then this run's and every sentence between them is RUN-01M2JA6J's, which is exactly what the shipped HTML holds today
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::TemplateRenderingTests::test_no_placeholder_and_no_prototype_literal_survives_a_render

### AC2: a section with no data renders NOT MEASURED by name, in both renderings

- **Given** a report built for a run with no forge access, no consult artefact and no token baseline, so the DORA, stakeholder-consult and cost sections each have no data
- **When** both renderings are produced
- **Then** all three sections are present with their headings in both; each body reads `NOT MEASURED` followed by the reason, naming the source it could not read; no absent figure renders as `0`, `-`, `None`, `n/a` or an empty cell anywhere in either output; and the two renderings carry the same ordered list of section headings, compared list against list
- **Mutant:** render an absent figure as an empty table cell - a reader then cannot separate a measured zero from a measurement nobody took, which is the one distinction this report exists to preserve, and the tables still line up
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::TemplateRenderingTests::test_an_empty_section_renders_not_measured_by_name_in_both

### AC3: the twin is committed beside the JSON and the HTML is generated on demand

- **Given** a PREPARE that has written its report
- **When** the tree under `sdlc-studio/` is listed, and `render --format html` is run with and without `--out`
- **Then** `sdlc-studio/reports/<id>.json` and `<id>.md` both exist and no `.html` file exists anywhere under `sdlc-studio/`; `render --format html` with no `--out` writes the page to stdout and creates no file; with `--out <path>` it writes only to that path, and a `--out` inside `sdlc-studio/reports/` is refused, naming D2a
- **Mutant:** write the HTML beside the twin at PREPARE time - a three-hundred-line generated page then churns in git on every re-prepare, which is the cost D2a's ruling was made to avoid
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::TemplateRenderingTests::test_the_twin_is_written_and_the_html_is_generated_on_demand

### AC4: the layout comes from the shipped template, not from strings in the renderer

- **Given** a fixture copy of `templates/core/sprint-report.md` with one section heading altered and one token added that the report has no figure for
- **When** the Markdown twin is rendered against that copy
- **Then** the output carries the altered heading, so the template is the source of the layout rather than its documentation; and the unfillable token makes the render exit non-zero naming that token, rather than leaving it in the output or silently emptying it
- **Mutant:** build the Markdown from format strings in the renderer and keep the template as documentation - the two drift on the first change to either, and the "shipped templates" in this story's title then describe nothing that runs
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::TemplateRenderingTests::test_the_layout_comes_from_the_shipped_template

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-17 | grooming 2026-09-17 | Groomed: four criteria, written against the defect the shipped templates carry: both were derived from a RUN-01M2JA6J prototype and still hold that run's facts in prose no token covers, so AC1 forbids the prototype literals as well as the unsubstituted tokens. NOT MEASURED is asserted in both renderings; D2a's on-demand HTML is held; the layout is proved to come from the template. |
