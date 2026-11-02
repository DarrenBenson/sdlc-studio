# US1111: v6.2.0 is cut: version, changelog, known issues, install pins and the specs' baseline

> **Status:** Done
> **Created:** 2026-11-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** package.json, package-lock.json, .claude/skills/sdlc-studio/templates/version.yaml, .claude/skills/sdlc-studio/SKILL.md, README.md, docs/INSTALL.md, sdlc-studio/prd.md, sdlc-studio/trd.md, sdlc-studio/tsd.md, CHANGELOG.md, changelog.d/, docs/known-issues.md, docs/release-notes-v6.2.0.md, tools/tests/test_lean_prd_refresh.py, tools/tests/test_lean_trd_refresh.py, tools/tests/test_lean_tsd_refresh.py, tools/tests/test_lean_release_cut_v62.py, .claude/skills/sdlc-studio/scripts/tests/test_bg0940_fragment_matches_sign.py
> **Epic:** EP0295
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** solo founder-engineer installing or upgrading (Maya)
**I want** v6.2.0 cut through the shipped release path: one version in every home, a CHANGELOG section composed from the fragments, a known-issues page derived from the corpus, install commands pinned to the new tag, and specs that name the release they cover
**So that** what I install, what the notes say, what the CHANGELOG lists and what the specs describe are the same release

## Acceptance Criteria

- **AC1:** Given the release commit, then every version home (package.json, package-lock.json, templates/version.yaml, the SKILL.md frontmatter, README, and the Version fields of prd.md, trd.md and tsd.md) carries 6.2.0, `check_versions.py --strict` exits 0, and the CHANGELOG holds a `## [6.2.0] - <date>` section composed by `release_cut.py changelog-cut` from every fragment present at the cut. Fails on: package.json left at 6.1.0, or a section merged by hand.
  - **Verify:** shell python3 -c 'import json,sys; core=json.load(open("package.json"))["version"].split("-"); sys.exit(tuple(map(int, core[0].split("."))) < (6, 2, 0))' && python3 tools/check_versions.py --strict && sed -n '/^## \[6\.2\.0\] - /,/^## \[6\.1\.0\] - /p' CHANGELOG.md | grep -q 'US1093'
  - **Verified:** yes (2026-11-02)
- **AC2:** Given `known_issues.py write --release 6.2.0` run at the cut, then `known_issues.py check` and `bar` exit 0 when judged at the commit that cut 6.2.0, the 6.2.0 notes carry exactly one filled `**v6.2.0 discloses N open defects: N Medium, N Low.**` line whose figures equal the page's, and the page no longer states the 6.1.0 release. Fails on: the 6.1.0 page left in place, or a count line that disagrees with the page.
  - **Verify:** pytest tools/tests/test_lean_release_cut_v62.py::ReleaseCutTests::test_the_known_issues_page_is_cut_for_620
  - **Verified:** yes (2026-11-02)
- **AC3:** Given README and docs/INSTALL.md, then every verified install and version example pins `--version v6.2.0`, README's 'New in 6' section links the 6.2.0 notes and its release-notes list calls 6.2.0, and only 6.2.0, the current release, and the 6.2.0 notes' CHANGELOG link is re-pointed from `#unreleased` to the 6.2.0 section. Fails on: a pin left at v6.1.0, or two releases called current.
  - **Verify:** shell grep -qE '[]][(]docs/release-notes-v6[.]2[.]0[.]md[)]' README.md && python3 -m pytest -q tools/tests/test_lean_public_docs_retired.py tools/tests/test_lean_release_cut_v62.py
  - **Verified:** yes (2026-11-02)
- **AC4:** Given the PRD, TRD and TSD after the cut, then each names v6.2.0 as the release it covers (no Coverage line reads `v6.1.0 as cut`), and the refresh tests of US1101 to US1104 read that baseline from the release the documents name and package.json rather than a literal, so they pass at 6.2.0 and still fail on their original mutants. Fails on: BASELINE left as the literal 6.1.0, or a refresh test that passes with the Coverage line removed.
  - **Verify:** shell python3 -m pytest -q tools/tests/test_lean_prd_refresh.py tools/tests/test_lean_trd_refresh.py tools/tests/test_lean_tsd_refresh.py
  - **Verified:** yes (2026-11-02)

## Notes

- Serves: Maya Okafor, End goal 1.
- Built LAST, as the release commit: depends on US1110 (the notes and their count line). Modelled on ddc3cda0, the v6.1.0 release commit, and US0985: bump the homes, `release_cut.py changelog-cut --version 6.2.0`, `known_issues.py write --release 6.2.0`, then `check_versions.py --strict`.
- `changelog.d/` is in Affects because the cut deletes every fragment, this unit's own included: `changelog.d/US1111.md` is written and then folded in the same commit.
- The criteria must stay true after later releases, because `gate.py --release` executes every story's Verify at each cut: the version test is 'at or above 6.2.0', the CHANGELOG range is bounded by the 6.1.0 heading, and AC2 judges the page at the commit that cut 6.2.0 (the v6.2.0 tag once it exists, else the commit that last wrote `docs/known-issues.md`), so a finding filed after the cut does not turn it red (BG1054).
- Measured at 519d125c, these tests name 6.1.0: `test_lean_prd_refresh.py` (`BASELINE`), `test_lean_trd_refresh.py` (`BASELINE`, `ON_MAIN`) and `test_lean_tsd_refresh.py` (`ON_MAIN`) pin the specs' baseline and are in Affects for AC4. `test_lean_release_notes_v61.py`, `test_lean_v61_last_lows.py`, `test_known_issues.py`, `test_lean_retired_handoff_surface.py`, `test_corpus_verify_env.py` and `test_release_prerelease.py` name 6.1.0 as history or a fixture and should pass unchanged; run each at the cut. A file outside Affects that needs a change is a finding to report, not an edit.
- The cut touches many test subjects, so run `tools/run-suite.sh all` (on the gate host) before review, and run US1101 to US1104's Verify lines through `verify_ac.py run --id <id>`.
- Out of this unit, after its review (D0395): `gate.py --release` exit 0, `release_cut.py record-green` and `tag-check`, the tag, the release workflow's publish, and the forward-port.
- Affects amended 2026-11-02, in flight (no command does this yet, CR0656): `test_bg0940_fragment_matches_sign.py` reads `changelog.d/BG0940.md` by path and has that fragment as its census subject, so the cut's fold of the fragment turns it red (the builder's `run-suite.sh all` on the gate host: 1 failed of 7313). It is re-pointed to read the entry from the fragment while it exists and from the released CHANGELOG section after the cut, keeping BG0945's and BG1035's mutants.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-02 | Claude Opus 5.5 (grooming) | Groomed for EP0295 under D0395: user story, criteria with Verify lines and notes, modelled on EP0273 |
| 2026-11-02 | Claude Opus 5.5 (grooming) | Affects amended in flight: the BG0940 fragment test, which the cut's fold turns red (see Notes) |
