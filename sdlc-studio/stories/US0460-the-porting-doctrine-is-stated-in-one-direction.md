# US0460: The porting doctrine is stated in one direction across the TRD and personas.md: the repo is source, the installed copy is the derived mirror

> **Status:** Review
> **Delivers:** CR0432
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/trd.md, sdlc-studio/personas.md, tools/tests/test_porting_doctrine.py
> **Epic:** EP0168
> **Points:** 5

## User Story

**As an** agent onboarding onto this repo and deciding where a fix should land first
**I want** the TRD's section 8 passages and personas.md to describe the forward-port flow the tooling enforces, with the inverted wording removed rather than merely outvoted
**So that** nobody edits the installed copy on the strength of a document that has been reversed since 2026-06-20

## Acceptance Criteria

### AC1: the docs name the repo as source, derived from the script

- **Given** tools/forward-port.sh, whose SRC is `.claude/skills/sdlc-studio` (:25) and whose TARGET defaults to `$HOME/.claude/skills/sdlc-studio` (:52), in that rsync argv order (:102-103)
- **When** the guard parses the direction out of the script and then reads the TRD Deployment Topology paragraph (trd.md:545-547), the Environment Strategy table (trd.md:549-555) and the personas.md Skill Maintainer card
- **Then** all three describe fixes landing in the repo and mirroring out, and name `forward-port.sh --check` as the drift gate; swapping SRC and TARGET in the script reddens the guard rather than leaving the docs unchallenged
- **Verify:** pytest tools/tests/test_porting_doctrine.py::PortingDoctrineAgrees::test_the_docs_name_the_repo_as_source_derived_from_the_script
- **Verified:** yes (2026-07-29)

### AC2: the inverted wording is absent, not merely outnumbered

- **Given** the six live back-port statements inside the Skill Maintainer card (personas.md:190 Primary Goal, :196-197 Background, :210 Needs, :216 Pain Points, :223 Typical Tasks, :231 Quote) and the two in the TRD (trd.md:545-547 and the :554 table row reading 'Production fix source; back-ported here')
- **When** the guard extracts the whole Skill Maintainer card block and the whole TRD section 8 block and applies an absence rule over each - no wording may make the installed copy the source of a fix
- **Then** no such wording survives in either block, and a fixture in which a back-port sentence is restored in any one of those subsections reddens the guard, so a repair cannot go green by adding one correct sentence above four inverted ones
- **Verify:** pytest tools/tests/test_porting_doctrine.py::PortingDoctrineAgrees::test_a_reintroduced_backport_sentence_in_any_subsection_reddens
- **Verified:** yes (2026-07-29)

### AC3: no bare router line count is quoted anywhere

- **Given** the stale figures in the 'AI Agent Executing the Skill' card (personas.md:144, '~195 lines') and the TRD Scaling Strategy passage (trd.md:558, '~260 lines') against a real SKILL.md of 270 lines and a 500-line ceiling that tools/check_budgets.py already enforces
- **When** the guard scans both files for a quoted SKILL.md line count
- **Then** it finds none, because both passages now cite the budgeted ceiling and its owning checker instead of a number that rots on every router edit; a reintroduced bare count fails, so there is one number with one owner rather than a tolerance nobody can set honestly
- **Verify:** pytest tools/tests/test_porting_doctrine.py::StaleFactsAreRefreshed::test_no_bare_router_line_count_is_quoted_in_personas_or_the_trd
- **Verified:** yes (2026-07-29)

### AC4: the scripts-only testing claim is refused while the tools suite exists

- **Given** the test modules under tools/tests/, counted from disk (33 today)
- **When** the guard reads the Skill Maintainer card's pain-point line about what has unit tests
- **Then** a claim that only the scripts have unit tests fails while that count is non-zero, so the claim is gated on the suite's existence rather than on someone noticing it
- **Verify:** pytest tools/tests/test_porting_doctrine.py::StaleFactsAreRefreshed::test_the_scripts_only_testing_claim_is_refused_while_the_tools_suite_exists
- **Verified:** yes (2026-07-29)

### AC5: a missing card, section or script fails rather than passing silently

- **Given** a fixture tree in which the Skill Maintainer heading is renamed, the TRD Environment Strategy heading is removed, or tools/forward-port.sh is absent
- **When** the guard tries to locate each block or parse the direction
- **Then** it fails naming what it could not read, and never returns a clean verdict derived from an empty extraction - the failure mode that would let this whole guard pass on a document it never opened
- **Verify:** pytest tools/tests/test_porting_doctrine.py::PortingDoctrineAgrees::test_a_missing_card_section_or_script_fails_rather_than_passing_silently
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
