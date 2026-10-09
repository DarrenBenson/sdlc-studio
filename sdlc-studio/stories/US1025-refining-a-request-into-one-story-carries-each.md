# US1025: Refining a request into one story carries each criterion's own Given, When, Then and Verify lines onto its AC

> **Status:** Draft
> **Delivers:** CR0618
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_refine_carries_verify.py, .claude/skills/sdlc-studio/reference-scripts-create.md, .claude/skills/sdlc-studio/help/refine.md, changelog.d/US1025.md
> **Epic:** EP0283
> **Points:** 5
> **Depends on:** BG0995
> **Persona:** Maya Okafor

## User Story

**As** the operator who grooms a change request before refining it
**I want** the Verify line, and any Given, When and Then lines, written beneath each request criterion to land on the matching AC of the story refine seeds
**So that** the checks I groomed on the request run on the story, instead of being re-typed by hand or silently dropped

## Acceptance Criteria

- **AC1:** Given two requests, a CR filed by `file_finding.py file --type cr` whose first criterion carries a Verify line and whose second carries none, and a hand-written request in the reverse order, when each is refined into one story (one by `--epic-title`, one `--into` an existing epic), then each criterion that carries a Verify line seeds `### ACn: <criterion>` with that line verbatim and no Given/When/Then placeholders, and each criterion without one keeps the full placeholder block.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine_carries_verify.py::RefineCarriesVerifyTests::test_each_criterion_keeps_its_own_verify_line
- **AC2:** Given a seeded story whose carried selector names a test the fixture holds, when `verify_ac.py run --id <story> --dry-run` runs, then its JSON report records that selector as the AC's verifier, and a pass.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine_carries_verify.py::RefineCarriesVerifyTests::test_the_runner_reads_the_carried_selector
- **AC3:** Given a request in the shape CR0413 to CR0417 carry, `- [ ] AC1: title` with unindented Given, When, Then and `- **Verify:**` lines beneath and a prose paragraph after the last criterion, when it is refined into one story, then each AC carries the request's own Given, When, Then and Verify lines verbatim, a criterion with no Verify line gets the placeholder Verify, and the trailing paragraph is not carried.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine_carries_verify.py::RefineCarriesVerifyTests::test_the_older_given_when_then_shape_is_carried
- **AC4:** Given a hand-written request whose criterion's Verify selector is a near miss of a test the fixture holds, when `refine.py apply` runs, then it refuses before anything is minted, naming the request, the criterion and the selector to fix, and points to `--no-seed-acs`; the same refine with `--no-seed-acs` mints.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine_carries_verify.py::RefineCarriesVerifyTests::test_a_mistyped_selector_is_refused_before_anything_is_minted
- **AC5:** Given the refine entry in reference-scripts-create.md and the grooming section of help/refine.md, when the test reads them and runs the refine they describe on a fixture, then both say a criterion's own lines are carried onto the seeded AC, neither says the Then is the criterion or that a multi-story breakdown gets a redistribute note, and the fixture's seed matches what they say.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine_carries_verify.py::RefineCarriesVerifyTests::test_the_catalogue_and_help_describe_what_the_seed_carries

## Notes

- Release: 6.2 (D0355 breakdown G9, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: today's seed (a placeholder Verify for every criterion); verifiers gathered into a list and paired by position, which only the hand-written request's order exposes, because the filer refuses a blank verifier ahead of a filled one; or the selector markdown-safed
- AC2 must fail on: the carried line written in a shape `verify_ac.parse_story` does not read under a heading block, such as an indented sub-bullet
- AC3 must fail on: a parser that reads only an indented Verify line, which drops this shape's grooming silently; or one that absorbs the trailing paragraph into the last criterion
- AC4 must fail on: carrying the line without `file_finding.check_verify_selectors`, so refine mints a story that `artifact.py new` would refuse
- AC5 must fail on: the docs left as they are: reference-scripts-create.md:239-242 and help/refine.md:59 are already false at HEAD
- Checked at HEAD (and by the panel): a CR filed with one `--verify` refines into one story whose ACs all read `- **Verify:** {{executable check}}`. `_CRITERION_RE` (refine.py:51) reads only the `- [ ]` line, and `_seed_acs` (refine.py:203) writes the placeholder block for every criterion.
- One definition of 'a criterion's lines' (LL0016): a block parser, `file_finding.criteria_blocks`, sits beside the writer `checklist_block` (file_finding.py:1426). For each `- [ ]` criterion it returns the criterion text and the Given, When, Then and Verify lines beneath it, indented or not, up to the next criterion or the first line that is neither. Refine calls it, and the validator bug below reads the same function, so the validator stays silent on exactly the lines refine carries.
- Seed rule (panel, Q1): carry what the request has. A criterion carrying none of the four lines keeps today's block exactly. One carrying a Verify line gets no Given/When/Then placeholders. One carrying Given/When/Then lines and no Verify gets the placeholder Verify. Carried lines are never markdown-safed (`artifact._verifiers_of`'s rule), and `Verified:` lines are never carried.
- Pre-mint check (panel, Q2): every carried selector goes through `file_finding.check_verify_selectors` before the first mint, from one refine helper that the CR0628 refusals story extends. Build it once. Only a typo is refused; a selector into a test module that does not exist yet is accepted, as `artifact.py new` accepts it. The filer already checks selectors at filing (file_finding.py:2167), so the fixture is a hand-written request.
- `_decompose` (refine.py:300-307) and `_decompose_into` (refine.py:388-393) each repeat the seeding branch; AC1 drives both. The existing test at test_refine.py:859 still holds: a criterion with no Verify keeps the placeholder.
- Builds after BG0995, so the fixture's headings are clean whatever label the criteria carry.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G9 after the refine panel's review |
