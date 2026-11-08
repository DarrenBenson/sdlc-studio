# US1139: v6.3.0 is cut: version, changelog, known issues, install pins and the specs' baseline

> **Status:** Draft
> **Created:** 2026-11-08
> **Created-by:** sdlc-studio new
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Affects:** package.json, package-lock.json, .claude/skills/sdlc-studio/templates/version.yaml, .claude/skills/sdlc-studio/SKILL.md, README.md, docs/INSTALL.md, sdlc-studio/prd.md, sdlc-studio/trd.md, sdlc-studio/tsd.md, CHANGELOG.md, changelog.d/, docs/known-issues.md, docs/release-notes-v6.3.0.md, tools/tests/test_lean_prd_refresh.py, tools/tests/test_lean_trd_refresh.py, tools/tests/test_lean_tsd_refresh.py, tools/tests/test_lean_release_cut_v63.py, tools/tests/test_lean_release_notes_v63.py
> **Epic:** EP0301
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** solo founder-engineer installing or upgrading (Maya)
**I want** v6.3.0 cut through the shipped release path: one version in every home, a CHANGELOG section composed from the fragments, a known-issues page derived from the corpus, install commands pinned to the new tag, and specs that name the release they cover
**So that** what I install, what the notes say, what the CHANGELOG lists and what the specs describe are the same release

## Acceptance Criteria

- **AC1:** Given the release commit, then every version home carries 6.3.0: package.json, package-lock.json, templates/version.yaml, the SKILL.md frontmatter, README, and the Version fields of prd.md, trd.md and tsd.md. `check_versions.py --strict` exits 0, and the CHANGELOG holds a `## [6.3.0] - <date>` section composed by `release_cut.py changelog-cut` from every fragment present at the cut. Fails on: package.json left at 6.2.0, or a section merged by hand.
  - **Verify:** shell python3 -c 'import json,sys; core=json.load(open("package.json"))["version"].split("-"); sys.exit(tuple(map(int, core[0].split("."))) < (6, 3, 0))' && python3 tools/check_versions.py --strict && sed -n '/^## \[6\.3\.0\] - /,/^## \[6\.2\.0\] - /p' CHANGELOG.md | grep -q 'US1126'
- **AC2:** Given `known_issues.py write --release 6.3.0` run at the cut, then `known_issues.py check` and `bar` exit 0 when judged at the commit that cut 6.3.0. The 6.3.0 notes carry exactly one filled `**v6.3.0 discloses N open defects: N Medium, N Low.**` line whose figures equal the page's, and the page no longer states the 6.2.0 release. Fails on: the 6.2.0 page left in place, or a count line that disagrees with the page.
  - **Verify:** pytest tools/tests/test_lean_release_cut_v63.py::ReleaseCutTests::test_the_known_issues_page_is_cut_for_630
- **AC3:** Given README and docs/INSTALL.md, then every verified install and version example pins `--version v6.3.0`. README links the 6.3.0 notes, and its release-notes list calls 6.3.0, and only 6.3.0, the current release. The 6.3.0 notes' CHANGELOG link is re-pointed from `#unreleased` to the 6.3.0 section. Fails on: a pin left at v6.2.0, or two releases called current.
  - **Verify:** shell grep -qE '[]][(]docs/release-notes-v6[.]3[.]0[.]md[)]' README.md && python3 -m pytest -q tools/tests/test_lean_public_docs_retired.py tools/tests/test_lean_release_cut_v63.py
- **AC4:** Given the PRD, TRD and TSD after the cut, then each names v6.3.0 as the release it covers (no Coverage line reads `v6.2.0 as cut`), and the refresh tests read that baseline from the release the documents name and package.json, so they pass at 6.3.0. Fails on: a refresh test that passes with the Coverage line removed.
  - **Verify:** shell python3 -m pytest -q tools/tests/test_lean_prd_refresh.py tools/tests/test_lean_trd_refresh.py tools/tests/test_lean_tsd_refresh.py
- **AC5:** Given the 6.3.0 release text after the cut, then three sentences the reviews found claiming more than the code does are corrected (D0432). (a) The notes' light-APPROVE bullet says a light APPROVE stops counting only once `critic.tier_for` derives `full` for the unit's risk band, and then when the tier was forced with `--tier light` or the Affects grew (conformance.py, the light-APPROVE check). (b) The notes' `--force` sentence no longer says it rewrites every file `init` writes: it leaves `sdlc-studio/.version` alone and skips an `_index.md` that exists (init.py). (c) BG1290's CHANGELOG entry says that `critic.self_check_gap` sets aside a commit whose subject names only another unit, so a change to the unit's Affects committed under another unit's id is not read as stale. Fails on: any of the three sentences as worded before the cut.
  - **Verify:** pytest tools/tests/test_lean_release_cut_v63.py::ReleaseCutTests::test_the_release_text_claims_no_more_than_the_code

## Notes

- Serves: Maya Okafor, End goal 1.
- Built LAST, as the release commit, after the notes, docs and specs stories and the five release bugs (D0427, D0428) are on main. Modelled on US1111: bump the homes, `release_cut.py changelog-cut --version 6.3.0`, `known_issues.py write --release 6.3.0`, then `check_versions.py --strict`.
- `changelog.d/` is in Affects because the cut deletes every fragment, this unit's own included: `changelog.d/<ID>.md` is written and then folded in the same commit.
- The criteria must stay true after later releases, because `gate.py --release` executes every story's Verify at each cut. The version test is 'at or above 6.3.0', the CHANGELOG range is bounded by the 6.2.0 heading, and AC2 judges the page at the commit that cut 6.3.0, so a finding filed after the cut does not turn it red (BG1054).
- Run `conformance.py check` on the whole workspace before review: a cut that deletes fragments can turn a Done light-tier unit full (the run-four trap). The cut touches many test subjects, so run `tools/run-suite.sh all` on the gate host before review. A file outside Affects that needs a change is a finding to report, not an edit.
- Out of this unit, after its review (D0427): `gate.py --release` exit 0 on the gate host, `release_cut.py record-green --commit <full sha>` and `tag-check`, the tag, the release workflow's publish, and the forward-port.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Created via `new` (deterministic) |
| 2026-11-08 | Claude Opus 5.5 (grooming) | Groomed for EP0301 under D0427: user story, criteria with Verify lines and notes, modelled on EP0295 |
| 2026-11-08 | Claude Opus 5.5 (grooming) | AC5 added under D0432: three over-claiming release-text sentences from the US1136 and BG1290 reviews; Points 3 to 5; `test_lean_release_notes_v63.py` joins Affects |
