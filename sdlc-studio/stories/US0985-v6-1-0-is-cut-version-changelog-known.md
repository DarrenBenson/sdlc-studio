# US0985: v6.1.0 is cut: version, changelog, known issues and install pins

> **Status:** Ready
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** package.json, package-lock.json, .claude/skills/sdlc-studio/templates/version.yaml, .claude/skills/sdlc-studio/SKILL.md, README.md, docs/INSTALL.md, sdlc-studio/prd.md, sdlc-studio/trd.md, sdlc-studio/tsd.md, CHANGELOG.md, changelog.d/, docs/known-issues.md, docs/release-notes-v6.1.0.md, changelog.d/US0985.md
> **Epic:** EP0273
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** solo founder-engineer installing or upgrading (Maya)
**I want** v6.1.0 cut through the shipped release path: one version in every home, a CHANGELOG section composed from the fragments, a known-issues page derived from the corpus, and install commands pinned to the new tag
**So that** what I install, what the notes say and what the CHANGELOG lists are the same release

## Acceptance Criteria

- **AC1:** Given the release commit, then every version home (package.json, package-lock.json, templates/version.yaml, the SKILL.md frontmatter, README, and the Version fields of prd.md, trd.md and tsd.md) carries 6.1.0 and `check_versions.py --strict` exits 0, and the CHANGELOG's `## [6.1.0] - <date>` section, composed by `release_cut.py changelog-cut --version 6.1.0`, holds the fragments' Breaking entries, with the fragments consumed. Fails on: package.json bumped alone (`--strict` names each home left at 6.0.0, the specs included); a hand-written `## [6.1.0]` heading over fragments still in `changelog.d/`, or fragments deleted without being folded, so the section lacks the handoff retirement
  - **Verify:** shell python3 -c 'import json,sys; core=json.load(open("package.json"))["version"].split("-"); sys.exit(tuple(map(int, core[0].split("."))) < (6, 1, 0))' && python3 tools/check_versions.py --strict && sed -n '/^## \[6\.1\.0\] - /,/^## \[6\.0\.0\] - /p' CHANGELOG.md | grep -q -- 'gate.py --require-handoff' && test ! -e changelog.d/US0978.md
- **AC2:** Given `known_issues.py write --release 6.1.0` run at the cut, then `known_issues.py check` and `bar` exit 0, the 6.1.0 notes carry exactly one filled `**v6.1.0 discloses N open defects: N Medium, N Low.**` line, and the page no longer states the 6.0 bar heading. Fails on: the 6.0.0 page left in place (its heading reads 'The bar v6.0 is held to' and `check` exits 1, as it does at HEAD); a page edited by hand; tagging over an open High
  - **Verify:** shell python3 tools/known_issues.py check && python3 tools/known_issues.py bar && test "$(grep -cE '^\*\*v6\.1\.0 discloses [0-9]+ open defects: [0-9]+ Medium, [0-9]+ Low\.\*\*$' docs/release-notes-v6.1.0.md)" = 1 && ! grep -qx '## The bar v6.0 is held to' docs/known-issues.md
- **AC3:** Given README and docs/INSTALL.md, then every verified install and version example pins `--version v6.1.0`, README's 'New in 6' section links the 6.1.0 notes and its release-notes list calls 6.1.0, and only 6.1.0, the current release; the 6.1.0 notes' CHANGELOG link is re-pointed from `#unreleased` to the `[6.1.0]` heading. Fails on: the version bumped with README and INSTALL still pinning `--version v6.0.0` or the list still calling 6.0.0 current (the front-door test reads the release from package.json and goes red); the notes still linking an emptied `[Unreleased]`
  - **Verify:** shell grep -qE '[]][(]docs/release-notes-v6[.]1[.]0[.]md[)]' README.md && python3 -m pytest -q tools/tests/test_lean_public_docs_retired.py tools/tests/test_lean_release_notes_v61.py

## Notes

- Built LAST in the sprint, as the release commit: Depends on US0983 (the notes and their count line) and US0984 (the specs it bumps). Modelled on 96bd94d1, the v6.0.0 release commit: bump the homes, `release_cut.py changelog-cut --version 6.1.0`, `known_issues.py write --release 6.1.0`, then `check` and `bar`, README and INSTALL pins. No rename this time: 6.0.0 had no candidate heading to move.
- `changelog.d/` is in Affects because the cut deletes every fragment, this unit's own included; `changelog.d/US0985.md` is written and then folded in the same commit.
- Each shell Verify was run at 6589fbf0 and is red for the right reason: AC1 on the version (package.json 6.0.0, below 6.1.0), AC2 on `known_issues.py check` exiting 1 (the page disagrees with the corpus) and the missing 6.1.0 notes, AC3 on README not linking the 6.1.0 notes. Positive control for AC1's version test: 6.1.0, 6.10.0 and 7.0.0 pass, 6.0.0 fails; a 6.1.0-rc.1 cut fails, having no `## [6.1.0]` heading.
- The criteria are written to stay true after later releases, because `gate.py --release` executes every story's Verify at each cut: the version test is 'at or above 6.1.0', the CHANGELOG range is bounded by the 6.0.0 heading, and the front-door test reads the current version from package.json. `known_issues.py check` and `bar` are release-boundary checks: between releases a filed finding reddens `check` (its docstring says so), and every later cut rewrites the page before the gate runs.
- Out of this unit, after the operator's signature (D0325): `gate.py --release` exit 0, `release_cut.py record-green` and `tag-check`, the tag, the GitHub release and the sdlc-studio.com update. The forward-port to the installed copy (`tools/forward-port.sh --yes`) follows the tag.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-03 | engineering seat (grooming) | Groomed for EP0273 under D0325: user story, three criteria with shell Verify lines run red at 6589fbf0, Affects modelled on the v6.0.0 release commit 96bd94d1 |
