# US1330: v6.5.0 is cut: version, changelog, known issues under the operator's bar, install pins, the specs' baseline and the evidence page

> **Status:** Ready
> **Depends on:** US1327, US1328, US1329
> **Release:** 6.5
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** package.json, package-lock.json, .claude/skills/sdlc-studio/templates/version.yaml, .claude/skills/sdlc-studio/SKILL.md, sdlc-studio/.version, README.md, docs/INSTALL.md, docs/enterprise.md, sdlc-studio/prd.md, sdlc-studio/trd.md, sdlc-studio/tsd.md, CHANGELOG.md, changelog.d/, changelog.d/US1330.md, docs/known-issues.md, docs/release-notes-v6.5.0.md, docs/evidence.md, tools/known_issues.py, tools/tests/test_known_issues.py, tools/tests/test_lean_prd_refresh.py, tools/tests/test_lean_trd_refresh.py, tools/tests/test_lean_tsd_refresh.py, tools/tests/test_lean_release_cut_v65.py
> **Epic:** EP0379
> **Points:** 8
> **Persona:** Abena Osei

## User Story

**As a** head of engineering whose teams install or upgrade to the release she takes to the change
board (Abena)
**I want** v6.5.0 cut through the shipped release path: one version in every home, this
repository's own project stamp included, a CHANGELOG section composed from the fragments, a
known-issues page that states the bar 6.5 was held to and shows it met, install commands pinned to
the new tag on every page that gives one, specs that name the release they cover, and an evidence
page that lists every signed run
**So that** what my teams install, what the notes say, what the CHANGELOG lists, what the
disclosure page claims and what the specs describe are the same release, and the board is shown
every defect it ships with against the bar it was promised

## Acceptance Criteria

- **AC1:** Given the release commit, then every version home carries 6.5.0: package.json,
  package-lock.json (its top `version` and its root package's), templates/version.yaml, the SKILL.md
  frontmatter, README, and the Version fields of prd.md, trd.md and tsd.md; `check_versions.py
  --strict` exits 0; this repository's `sdlc-studio/.version` names skill_version 6.5.0, written by
  `migrate.py --apply`'s own step, not by hand; and the CHANGELOG holds a `## [6.5.0] - <date>`
  section composed by `release_cut.py changelog-cut` from every fragment present at the cut,
  after `changelog.d/US1054.md` is corrected to the state BG1655 left, so the section no longer says a
  copy naming "the Primary persona, Sam the new shopper" is refused in every project whose cast holds
  no Sam. Fails on: package.json, every other home and `.version` at 6.4.0, and no `[6.5.0]`
  heading, as at HEAD; a section merged by hand; or a `[6.5.0]` section that still carries
  US1054's last sentence. The test reads package.json's version as at or above 6.5.0, package-lock.json's top
  and root-package versions as equal to it, `sdlc-studio/.version`'s skill_version as at or above 6.5.0, and the
  CHANGELOG range from the `[6.5.0]` heading to the `[6.4.0]` heading as holding US1321 (rechecked at the cut) and
  not the sentence ending 'in every project whose cast holds no Sam'.
  - **Verify:** shell python3 tools/check_versions.py --strict && python3 -m pytest -q tools/tests/test_lean_release_cut_v65.py::ReleaseCutTests::test_every_version_home_and_the_section_name_650
- **AC2:** Given `known_issues.py write --release 6.5.0` run at the cut, then, judged at the commit
  that cut 6.5.0, `known_issues.py check` exits 0, the page's heading names the v6.5 bar and states
  it as D0560 rules it (fewer than 50 open defects and none at Medium or above), which needs a 6.5
  entry in `tools/known_issues.py`'s `BARS` with the v6.0 bar kept as history, and the 6.5.0 notes
  carry exactly one filled `**v6.5.0 discloses N open defects: N Medium, N Low.**` line whose figures
  equal the page's. Fails on: the page at HEAD, cut for v6.4 with 369 findings (65 Medium);
  `known_issues.render(REPO, "6.5.0")` at HEAD, which heads "The bar v6.5 is held to" with v6.0's
  sentence, "Zero open Critical or High finding at the tag, and every open Medium ruled by one triage
  decision"; or a count line that disagrees with the page.
  - **Verify:** pytest tools/tests/test_lean_release_cut_v65.py::ReleaseCutTests::test_the_known_issues_page_is_cut_for_650
- **AC3:** Given the bug corpus at the commit that cut 6.5.0, then `known_issues.py bar` judged
  there exits 0 (`bar --at v6.5.0` once the tag exists, the working tree before it), and the
  operator's bar holds there: the test counts the open findings in that commit's corpus and finds
  fewer than 50, and none at Medium, High or Critical. Fails on: the commit that last wrote
  docs/known-issues.md at HEAD (cd0e478ec, the 6.4.0 page), whose corpus holds 369 open findings, 65
  of them Medium; `bar --at v6.5.0` at HEAD, which exits 2 because no such tag exists; or a cut made
  while 50 or more findings, or any at Medium or above, are open.
  - **Verify:** pytest tools/tests/test_lean_release_cut_v65.py::ReleaseCutTests::test_the_release_bars_hold_at_the_cut
- **AC4:** Given README, docs/INSTALL.md and docs/enterprise.md, then every install and version
  example pins `--version v6.5.0` (`-Version v6.5.0` in PowerShell); README links the 6.5.0 notes
  and its release-notes list calls 6.5.0, and only 6.5.0, the current release; and the 6.5.0 notes'
  CHANGELOG link is re-pointed from `#unreleased` to the 6.5.0 section. Fails on: README and INSTALL
  pinned at v6.4.0, and enterprise.md's "Pin a release" line at `v6.4.0`, which no test reads, as at
  HEAD; two releases called current.
  - **Verify:** shell grep -qE '[]][(]docs/release-notes-v6[.]5[.]0[.]md[)]' README.md && python3 -m pytest -q tools/tests/test_lean_public_docs_retired.py tools/tests/test_lean_release_cut_v65.py::ReleaseCutTests::test_the_notes_link_the_650_section tools/tests/test_lean_release_cut_v65.py::ReleaseCutTests::test_every_install_pin_names_the_release
- **AC5:** Given the PRD, TRD and TSD at the commit that cut 6.5.0, then each Coverage line, and the
  PRD's inventory baseline, reads v6.5.0 as cut, plus the 6.6 work on `main`; the refresh tests read
  that baseline from package.json through `release_baseline()` and refuse the stale "v6.4.0 as cut,
  plus the 6.5 work" as they refuse 6.3's. Fails on: the specs at HEAD, whose Coverage lines read
  v6.4.0 as cut; a refresh test that passes with the 6.4.0 baseline put back.
  - **Verify:** shell python3 -m pytest -q tools/tests/test_lean_release_cut_v65.py::ReleaseCutTests::test_the_specs_name_650_as_cut tools/tests/test_lean_prd_refresh.py tools/tests/test_lean_trd_refresh.py tools/tests/test_lean_tsd_refresh.py
- **AC6:** Given docs/evidence.md, then it is regenerated with `sprint_report.py evidence --out
  docs/evidence.md` and lists every signed report through RPT0045 at least, and `--check` exits 0.
  Fails on: the page at HEAD, whose newest report is RPT0035 and on which `--check` notes RPT0036 to
  RPT0045 as not yet on the page.
  - **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/sprint_report.py evidence --out docs/evidence.md --check && grep -q 'RPT0045' docs/evidence.md

## Notes

- Serves: Abena Osei, End goals 1 and 3 (quoted under US1327).
- Built LAST, as the release commit, after US1327, US1328 and US1329 are on main. Modelled on
  US1173: bump the homes, `release_cut.py changelog-cut --version 6.5.0`, `known_issues.py write
  --release 6.5.0`, `migrate.py --apply` for `.version`, `sprint_report.py evidence --out
  docs/evidence.md`, then `check_versions.py --strict`.
- `.version` (BG1301, Won't Fix): the cut restamps it through `migrate.py --apply`, as the D0500
  commit did for 6.4.0. Rehearsed at grooming on a copy of this workspace with the skill's version
  read as 6.5.0: the dry run lists one deterministic upgrade, `sdlc-studio/.version stale (skill
  6.4.0 -> 6.5.0)`; `--apply` changes only that file (skill_version "6.5.0", upgraded_from 6.4.0),
  after which `migrate` reports `0 deterministic upgrade(s)`, as US0926::AC1 needs at the release
  gate. This repository sets `personas.standard: block`, so `--apply` writes no persona key here.
- Test modules: `grep -rln "6\.4\.0"` finds nine (test_check_versions, test_lean_release_cut_v64,
  test_lean_release_notes_v64, test_lean_specs_v64, test_lean_trd_refresh, test_pre_push_hook,
  test_escape_trace, test_evidence_pack_build, test_release_cut). None pins the live baseline: each
  uses 6.4.0 as a fixture literal or judges the v6.4.0 tag, and all passed in a clone with every
  version home moved to 6.5.0. That rehearsal turned red only test_lean_prd_refresh (2 tests),
  test_lean_trd_refresh (1, the `[6.5.0]` heading), test_lean_tsd_refresh (1) and
  test_lean_public_docs_retired (2, the pins and the README notes link), each cleared by this
  unit's own edits. The three refresh tests are in Affects to add the stale 6.4.0 mutant, as US1173
  added 6.3.0's; test_lean_public_docs_retired reads the release from package.json and needs no edit.
- `tools/known_issues.py` and `tools/tests/test_known_issues.py` are in Affects for AC2's `BARS`
  entry. Without it the 6.5.0 page states the v6.0 bar under a v6.5 heading, which is weaker than
  the bar 6.5 was held to. `bar` itself stays Critical and High (its `BARRED`); the stricter count
  is the cut test's, as the grooming brief asked. Existing `test_known_issues` cases render 5.1.1,
  6.0.0 and 6.1.0 and are unaffected by a (6, 5) entry; add one for 6.5.0.
- docs/enterprise.md is in Affects because line 59 pins `--version v6.4.0` and no test reads it
  (`test_lean_public_docs_retired` reads README, CONTRIBUTING and INSTALL only). AC4's new test
  holds it to package.json's release so a later cut cannot leave it behind.
- AC1's id: the cut composes fragment text, not ids, so pick an id a fragment's own text carries.
  At grooming a rehearsed cut on a copy put US1321 (and CR0748) in the `[6.5.0]` section and left
  US1036 and US1326 out; recheck before the cut.
- Before the cut, correct `changelog.d/US1054.md`: its last sentence says a copy naming "the
  Primary persona, Sam the new shopper" is reported as `seat-persona-unknown`, which blocks, and
  BG1655 (committed after it) made a lone first name after a comma no claim. On a fixture holding
  the 6.4.0 cards verbatim with a cast of only Maya Okafor, `validate.py seats` reports errors=0
  warnings=0 and `persona_review.py check` blocks=0. A released CHANGELOG section is never
  rewritten, so this is the last point to fix it. `changelog.d/` is in Affects.
- At grooming the rehearsed `changelog-cut` printed nine `persona review owed:` lines, one per card
  this repository holds (none has a persona review row), and exited 0 (US1057's advice). It does
  not refuse; the operator may want the reviews before the tag.
- The criteria must stay true after later releases, because `gate.py --release` executes every
  story's Verify at each cut: the version tests read 'at or above 6.5.0', the CHANGELOG range is
  bounded by the 6.4.0 heading, AC2, AC3 and AC5 judge the commit that cut 6.5.0 (the tag once it
  exists, else the working tree while the cut is uncommitted, else the commit that last wrote the
  page), and AC6 reads 'RPT0045 at least'.
- Run `conformance.py check` on the whole workspace and `tools/run-suite.sh all` on the gate host
  before review. A file outside Affects that needs a change is a finding to report, not an edit.
- Out of this unit, after its review and the run's sign (D0545 leaves the tag, the publish and the
  site to the operator): `release_cut.py evidence-pack --version 6.5.0 --reports
  RPT0035,RPT0036,RPT0037,RPT0038,RPT0039,RPT0040,RPT0041,RPT0042,RPT0043,RPT0044,RPT0045` plus run
  twenty-seven's report once signed; a fresh `sprint_report.py evidence` and `known_issues.py write
  --release 6.5.0` if anything was signed or filed after the cut (as D0500 did for 6.4.0);
  `gate.py --release` exit 0 on the gate host; `release_cut.py record-green --commit <full sha>` and
  `tag-check`; the tag, the release workflow's publish, the forward-port and the site.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-25 | orchestrator (delegate under D0545) | Groomed for EP0379 from the product seat's draft (run twenty-seven, the v6.5.0 release epic): user story, criteria with Verify lines, Release 6.5, Depends on for the wave order, and notes, modelled on EP0314 |
