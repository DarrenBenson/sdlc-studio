# US1173: v6.4.0 is cut: version, changelog, known issues, install pins and the specs' baseline

> **Status:** Done
> **Depends on:** US1170, US1171, US1172, BG1487, BG1493, BG1494
> **Release:** 6.4
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio new
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Affects:** package.json, package-lock.json, .claude/skills/sdlc-studio/templates/version.yaml, .claude/skills/sdlc-studio/SKILL.md, README.md, docs/INSTALL.md, sdlc-studio/prd.md, sdlc-studio/trd.md, sdlc-studio/tsd.md, CHANGELOG.md, changelog.d/, changelog.d/US1173.md, docs/known-issues.md, docs/release-notes-v6.4.0.md, tools/tests/test_lean_prd_refresh.py, tools/tests/test_lean_trd_refresh.py, tools/tests/test_lean_tsd_refresh.py, tools/tests/test_lean_release_cut_v64.py, tools/tests/test_lean_release_notes_v64.py
> **Epic:** EP0314
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** head of engineering whose teams install or upgrade to the release she takes to the change board (Abena)
**I want** v6.4.0 cut through the shipped release path: one version in every home, a CHANGELOG section composed from the fragments, a known-issues page derived from the corpus with no barred finding open, install commands pinned to the new tag, and specs that name the release they cover
**So that** what my teams install, what the notes say, what the CHANGELOG lists and what the specs describe are the same release, and the board is shown every defect it ships with

## Acceptance Criteria

- **AC1:** Given the release commit, then every version home carries 6.4.0: package.json, package-lock.json, templates/version.yaml, the SKILL.md frontmatter, README, and the Version fields of prd.md, trd.md and tsd.md. `check_versions.py --strict` exits 0, and the CHANGELOG holds a `## [6.4.0] - <date>` section composed by `release_cut.py changelog-cut` from every fragment present at the cut. Fails on: package.json left at 6.3.0, or a section merged by hand.
  - **Verify:** shell python3 -c 'import json,sys; core=json.load(open("package.json"))["version"].split("-"); sys.exit(tuple(map(int, core[0].split("."))) < (6, 4, 0))' && python3 tools/check_versions.py --strict && sed -n '/^## \[6\.4\.0\] - /,/^## \[6\.3\.0\] - /p' CHANGELOG.md | grep -q 'US1164'
  - **Verified:** yes (2026-11-16)
- **AC2:** Given `known_issues.py write --release 6.4.0` run at the cut, then `known_issues.py check` exits 0 when judged at the commit that cut 6.4.0. The 6.4.0 notes carry exactly one filled `**v6.4.0 discloses N open defects: N Medium, N Low.**` line whose figures equal the page's, and the page no longer states the 6.3.0 release. Fails on: the 6.3.0 page left in place, or a count line that disagrees with the page.
  - **Verify:** pytest tools/tests/test_lean_release_cut_v64.py::ReleaseCutTests::test_the_known_issues_page_is_cut_for_640
  - **Verified:** yes (2026-11-16)
- **AC3:** Given the bug corpus at the cut, then `python3 tools/known_issues.py bar` exits 0: no finding at a barred severity is open, BG1493 (High) having been Fixed before the cut. Fails on: a cut made while BG1493, or any other finding at a barred severity, is open.
  - **Verify:** shell python3 tools/known_issues.py bar
  - **Verified:** yes (2026-11-16)
- **AC4:** Given README and docs/INSTALL.md, then every verified install and version example pins `--version v6.4.0`. README links the 6.4.0 notes, and its release-notes list calls 6.4.0, and only 6.4.0, the current release. The 6.4.0 notes' CHANGELOG link is re-pointed from `#unreleased` to the 6.4.0 section. Fails on: a pin left at v6.3.0, or two releases called current.
  - **Verify:** shell grep -qE '[]][(]docs/release-notes-v6[.]4[.]0[.]md[)]' README.md && python3 -m pytest -q tools/tests/test_lean_public_docs_retired.py tools/tests/test_lean_release_cut_v64.py
  - **Verified:** yes (2026-11-16)
- **AC5:** Given the PRD, TRD and TSD after the cut, then each names v6.4.0 as the release it covers (no Coverage line reads `v6.3.0 as cut`), and the refresh tests read that baseline from the release the documents name and package.json, so they pass at 6.4.0. Fails on: a refresh test that passes with the Coverage line removed.
  - **Verify:** shell python3 -m pytest -q tools/tests/test_lean_prd_refresh.py tools/tests/test_lean_trd_refresh.py tools/tests/test_lean_tsd_refresh.py
  - **Verified:** yes (2026-11-16)

## Notes

- Serves: Abena Osei, End goals 1 and 3.
- Built LAST, as the release commit, after US1170, US1171, US1172, BG1487, BG1493 and BG1494 are on main (D0474). Modelled on US1139: bump the homes, `release_cut.py changelog-cut --version 6.4.0`, `known_issues.py write --release 6.4.0`, then `check_versions.py --strict`.
- AC3 needs BG1493 (High) Fixed first: at grooming `known_issues.py bar` exits 1 with 'release bar NOT met: 1 open finding(s) at a barred severity - BG1493 (High)'. A High filed during run fifteen also holds the cut until it is fixed or ruled in a recorded decision.
- `changelog.d/` is in Affects because the cut deletes every fragment, this unit's own included: `changelog.d/US1173.md` is written and then folded in the same commit.
- The criteria must stay true after later releases, because `gate.py --release` executes every story's Verify at each cut. The version test is 'at or above 6.4.0', the CHANGELOG range is bounded by the 6.3.0 heading, and AC2 judges the page at the commit that cut 6.4.0, so a finding filed after the cut does not turn it red (BG1054). AC3's `bar` reads the live corpus, and holds at every later cut because the bar must be met there too.
- Run `conformance.py check` on the whole workspace before review: a cut that deletes fragments can turn a Done light-tier unit full (the run-four trap). The cut touches many test subjects, so run `tools/run-suite.sh all` on the gate host before review. A file outside Affects that needs a change is a finding to report, not an edit.
- Out of this unit, after its review and the run's sign (D0479: the tag and its publication stay with the operator): `release_cut.py evidence-pack --version 6.4.0 --reports RPT0028,RPT0029,RPT0030,RPT0031,RPT0032,RPT0033` plus run fifteen's report once signed, `gate.py --release` exit 0 on the gate host, `release_cut.py record-green --commit <full sha>` and `tag-check`, the tag, the release workflow's publish, the forward-port and the site.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | Claude Opus 5.5 | Created via `new` (deterministic) |
| 2026-11-16 | Claude Opus 5.5 (grooming) | Groomed for EP0314 under D0474: user story, criteria with Verify lines, Release 6.4, Depends on for the wave order, and notes, modelled on EP0301 |
