# CR-0405: CHANGELOG entries are hand-edited into a structured file with no helper and no structural check, so a bad insert silently reparents existing entries

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** CHANGELOG.md,tools/check_links.py,.claude/skills/sdlc-studio/scripts/artifact.py
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson; human; operator observation at the RUN-01KY3MFX close, filed by Claude Opus 4.8

## Summary

Hit twice in RUN-01KY3MFX. This project's rule is to use the deterministic tooling and never hand-roll what it wires - `artifact.py` mints an artefact with its id and index row, `file_finding.py` files a finding, `transition.py` changes a status - and every one of those exists because hand-editing a structured file goes wrong. CHANGELOG.md is a structured file (release sections, then Added / Fixed / Breaking subsections) with NO helper and NO structural check, so every entry is hand-inserted. The author inserted a block that began with its own `### Added` heading and ended with `### Fixed`, which silently reparented the whole existing Added list under the new Fixed heading. Nothing caught it: markdownlint flagged only an unrelated double blank line, and the error was found by reading the file. Recovery cost a `git checkout` and a full re-do. A second attempt then produced MD012 twice more, because inserting at a section boundary and getting the surrounding blank lines right is fiddly by hand and by nothing else. The failure is silent and structural: entries end up under the wrong heading, and a reader of the release notes is told a fix was an addition.

## Impact

Every commit in this project and in any consuming project that keeps a changelog, because the rule is that every behaviour change carries its entry in the same commit. The consequence of a bad insert is a release note that misfiles work under the wrong heading, which is exactly the kind of quiet wrongness the rest of this repo builds tooling to prevent - and it is the only structured file left where the answer is 'edit it carefully'.

## Acceptance Criteria

- [ ] A helper adds an entry to the named section of the [Unreleased] release, creating the subsection if it is absent, so a caller never positions text by hand.
- [ ] A structural check fails when a release section's subsection headings are out of order, duplicated within one release, or when a subsection is empty - the shapes a bad hand-insert produces.
- [ ] The check runs in the existing gate rather than as a step someone must remember, following the rule that a gate belongs in the command people actually run.
- [ ] The helper is idempotent enough to re-run: adding the same entry twice is refused or reported, never silently duplicated.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | Darren Benson | Raised |
