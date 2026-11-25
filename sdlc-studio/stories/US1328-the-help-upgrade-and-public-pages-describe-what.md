# US1328: The help, upgrade and public pages describe what 6.5 ships

> **Status:** Ready
> **Release:** 6.5
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/help/upgrade.md, .claude/skills/sdlc-studio/help/persona.md, .claude/skills/sdlc-studio/help/bug.md, .claude/skills/sdlc-studio/help/reconcile.md, .claude/skills/sdlc-studio/help/review.md, README.md, llms.txt, docs/existing-users.md, docs/engineering-leaders.md, tools/tests/test_lean_docs_v65.py, tools/tests/test_lean_docs_v64.py, tools/tests/test_lean_docs_v63.py, tools/tests/test_engineering_leaders_page.py, changelog.d/US1328.md
> **Epic:** EP0379
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** head of engineering reading the docs before her teams adopt 6.5 (Abena)
**I want** the help pages to name each refusal 6.5 adds where a user meets it, the upgrade page to
give the 6.4 to 6.5 path, and the public pages to say what 6.5 adds and how a delegated signature
is disclosed
**So that** no page sends my teams into a refusal it never mentioned, and the board can see who
answered for a run signed under delegation

## Acceptance Criteria

- **AC1:** Given the help pages a 6.4 user meets a 6.5 refusal from, then: help/upgrade.md's
  Prerequisites names Python 3.10+ with PyYAML and `python3 -m pip install pyyaml`, and says the
  installers, `gate.py` and every command reading a present `.config.yaml` refuse without it
  (US1296, US1297, US1298); help/persona.md names `personas.standard`, whose default `block` refuses
  a project card that breaks a blocking rule or whose latest review failed, whose `report` frames it
  and prints one `persona card blocked (report mode):` line, and which `migrate --apply` sets to
  `report` for a project holding its own cards with no value set, linking `reference-config.md` and
  `reference-persona.md#persona-rules` (US1322); help/bug.md says `file_finding.py file` refuses a
  finding that shares every declared `Affects` path with an artefact of its type and scores at or
  above the duplicate bar, exiting 1 and writing nothing, and that `--distinct-from <id>` files it
  anyway and is recorded as a `Distinct-from` line (US1324); and help/reconcile.md's What It Fixes
  table names `risk-class` drift, `apply` raising a story's `Risk-class` stamp to the map's class and
  never lowering one, linking `reference-reconcile.md#risk-class` (US1314). Each statement is checked
  against the command's own output on a fixture. Fails on: the four pages at HEAD, which name none
  of PyYAML, `personas.standard`, `--distinct-from` or `risk-class`.
  - **Verify:** pytest tools/tests/test_lean_docs_v65.py::DocsV65Tests::test_the_help_pages_name_the_refusals_65_adds
- **AC2:** Given help/review.md's section on the author's self-check, then it names
  `mutation.py run --edits <list.json> --scope <id>` (each edit applied in a scratch copy, one
  verdict line each: killed, survived, not-applied or error), `critic.py self-check record
  --mutants-from <report>` and the list it keeps in `sdlc-studio/reviews/author-mutants/<id>.json`,
  and says that `critic.py brief` replays that list against the tree, marks a mutant whose replayed
  verdict differs from its recorded one, and labels the replay the author's, not the reviewer's own
  mutation pass (US1200, US1201, US1202), linking `reference-review.md#author-self-check`. Fails on:
  help/review.md at HEAD, whose self-check section shows only `--claims claims.json --mutants
  mutants.json`.
  - **Verify:** pytest tools/tests/test_lean_docs_v65.py::DocsV65Tests::test_the_review_help_names_the_authors_replayed_mutants
- **AC3:** Given README.md, llms.txt and docs/engineering-leaders.md, then README has one 'New in
  6.5' line naming what 6.5 adds (a release held to fewer than 50 open defects and none at Medium or
  above, linking docs/known-issues.md; every persona and seat card held to a written standard; and a
  delegated signature that names the decision authorising it); llms.txt links docs/known-issues.md;
  and the Signer bullet of engineering-leaders.md says a signature may be entered under delegation
  only with `--decision` naming an accepted decision in `sdlc-studio/decisions.md`, and that the
  report's Signed by cell and the evidence pack's Accountable line then name the delegation and the
  decision (US1291, US1292), checked against a signed report's own cell. Fails on: README with no
  6.5 line, llms.txt with no link to the known-issues page, and a Signer bullet that names no
  delegation, all three as the pages stand at HEAD.
  - **Verify:** pytest tools/tests/test_lean_docs_v65.py::DocsV65Tests::test_the_public_pages_name_what_65_adds
- **AC4:** Given docs/existing-users.md, then it has a 'From 6.4 to 6.5' section, first, above 'From
  6.3 to 6.4'. It says: install PyYAML before reinstalling; `migrate`, then `migrate --apply`, owes a
  6.4 project its version stamp, sets `personas.standard: report` for a project holding its own
  cards, and removes `require_ac_verification` where it is set, each checked by running `migrate` on
  a 6.4-shaped fixture; to switch the standard on, run `persona_review.py check` and set
  `personas.standard: block` once it holds no card; and the four keys 6.5 adds are optional, each
  with the default `reference-config.md` states for it. test_lean_docs_v64's upgrade-page check
  finds its section by name, as test_lean_docs_v63's does, so it passes with 6.5's section above
  it. Fails on: the page at HEAD, whose newest section is 'From 6.3 to 6.4'; and
  test_lean_docs_v64's `froms[:4]` check, which refuses any section above 6.4's (run at grooming on a
  copy with a 6.5 heading inserted).
  - **Verify:** pytest tools/tests/test_lean_docs_v65.py::DocsV65Tests::test_existing_users_has_the_64_to_65_upgrade_path
- **AC5:** Given the changed pages, then README carries its 'New in 6.5' line within
  test_readme_front_door's 1,500-word ceiling, the 6.3 and 6.4 docs tests still pass, and
  `tools/check_links.py`, `tools/lint-style.sh` and `tools/check_budgets.py` pass. Fails on: README
  with no 'New in 6.5' line (as at HEAD), a README over 1,500 words (it is 1,498 at HEAD), a broken
  anchor, or an em dash.
  - **Verify:** shell grep -qE '^- \*\*New in 6\.5' README.md && python3 -m pytest -q tools/tests/test_readme_front_door.py tools/tests/test_lean_docs_v63.py tools/tests/test_lean_docs_v64.py && python3 tools/check_links.py && bash tools/lint-style.sh && python3 tools/check_budgets.py

## Notes

- Serves: Abena Osei, End goals 1 and 2 (quoted under US1327), and Maya Okafor (Secondary) on
  the upgrade path.
- Built in wave one. README's Version line, install pins, current-release line and release-notes
  list are the cut's (US1330's AC4): leave them at 6.4.0.
- README is 1,498 of the 1,500 words `test_readme_front_door.py` allows. Room for the 6.5 line
  comes from shortening the 6.3 and 6.4 lines, keeping every phrase their tests read:
  test_lean_docs_v64 reads "evidence pack", "change board", "`release_cut.py evidence-pack`", "each
  review seat's record", "`retro.py seats`", "escaped defect", "approval that missed it",
  "`escape.py trace`", "forecast" and "actual"; test_lean_docs_v63 reads one paragraph holding "US
  dollars", each metered harness's name, "per point", "`sprint lane run --harness <h>`" and
  "headless". Removing the 6.3 line outright fails test_lean_docs_v63 (run at grooming), which is
  why that test is in Affects: amend it only if no shortening fits.
- Check each help statement against the code's own output on a fixture, not by grepping the page
  alone: the refusal of a duplicate finding, the `persona card blocked (report mode):` line, the
  upgrade's `set personas.standard: report` and the gate's PyYAML refusal were each run at grooming
  (Evidence D1).
- help/sprint.md already names `sprint drive`, `lane land --resume`, `lane brief --repair`, `sign
  --delegated --decision` and the closed-run exception (US1196, US1193, US1195, US1293), and
  help/gate.md names `--red-run` and the `ci` keys (US1237, US1238): not in Affects. docs/INSTALL.md,
  docs/harnesses.md, docs/enterprise.md and llms.txt's harness lines were written by US1296 and
  US1315 to US1320: link them, do not restate them. docs/evidence.md is regenerated by the cut.
- Each test names its mutant first: the page as it stands at grooming (HEAD c6e8cc7a0) must fail
  it. The 6.5 test finds every section by name, never by position, so a later release's section
  above it does not turn it red at that release's gate.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-25 | orchestrator (delegate under D0545) | Groomed for EP0379 from the product seat's draft (run twenty-seven, the v6.5.0 release epic): user story, criteria with Verify lines, Release 6.5, Depends on for the wave order, and notes, modelled on EP0314 |
| 2026-11-25 | orchestrator (delegate under D0545) | Affects widened at the builder's BLOCKED: test_engineering_leaders_page.py holds every sentence of the page that names an agent or accountability as a closed set, and AC3's Signer sentence names the evidence pack's Accountable line |
