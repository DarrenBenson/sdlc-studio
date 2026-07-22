# CR-0405: CHANGELOG entries are hand-edited into a structured file with no helper and no structural check, so a bad insert silently reparents existing entries

> **Status:** In Progress
> **Decomposed-into:** EP0112
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/changelog.py,.claude/skills/sdlc-studio/scripts/gate.py,CHANGELOG.md
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson; human; operator observation at the RUN-01KY3MFX close, filed by Claude Opus 4.8

## Summary

**CORRECTED 2026-07-22, before refinement. The premise below was false and the title still carries it.**
This CR was filed asserting CHANGELOG.md has NO helper. It has one. `scripts/changelog.py` was
built for exactly this failure under LL0004's same-commit paperwork rule: each unit writes a
fragment under `changelog.d/`, `compose` folds every fragment into `## [Unreleased]` under its
declared section, CREATES a missing section heading (`changelog.py`:103), consumes the fragment
so a re-run cannot duplicate it, and refuses loudly before writing anything when a fragment
cannot be placed. `gate.py`:1252 already fails a release cut while a stray fragment exists. Three
of the four acceptance criteria below were therefore already met when this was filed, and the
check was verified by reading the source rather than assumed.

What actually happened in RUN-01KY3MFX is the more useful finding: the author hand-edited a file
that had a deterministic writer, twice, and then filed a CR asserting the writer did not exist.
That is this project's own signature failure - work done before establishing the contract it
depends on - occurring inside a change request about hand-editing structured files, which was
itself written by hand. The original filing is kept verbatim below rather than deleted, because
the CR is now partly evidence about how the claim was made.

**The remaining genuine gap** is one criterion, plus one the filing missed. There is no structural
check over CHANGELOG.md's OWN headings, so a hand-insert that reparents entries is still caught by
nothing; and nothing makes the hand-edit path visibly wrong while `changelog.d/` is live, which is
the step that would have prevented both incidents.

**Original filing, as raised:** Hit twice in RUN-01KY3MFX. This project's rule is to use the deterministic tooling and never hand-roll what it wires - `artifact.py` mints an artefact with its id and index row, `file_finding.py` files a finding, `transition.py` changes a status - and every one of those exists because hand-editing a structured file goes wrong. CHANGELOG.md is a structured file (release sections, then Added / Fixed / Breaking subsections) with NO helper and NO structural check, so every entry is hand-inserted. The author inserted a block that began with its own `### Added` heading and ended with `### Fixed`, which silently reparented the whole existing Added list under the new Fixed heading. Nothing caught it: markdownlint flagged only an unrelated double blank line, and the error was found by reading the file. Recovery cost a `git checkout` and a full re-do. A second attempt then produced MD012 twice more, because inserting at a section boundary and getting the surrounding blank lines right is fiddly by hand and by nothing else. The failure is silent and structural: entries end up under the wrong heading, and a reader of the release notes is told a fix was an addition.

## Impact

Every commit in this project and in any consuming project that keeps a changelog, because the rule is that every behaviour change carries its entry in the same commit. The consequence of a bad insert is a release note that misfiles work under the wrong heading, which is exactly the kind of quiet wrongness the rest of this repo builds tooling to prevent - and it is the only structured file left where the answer is 'edit it carefully'.

## Acceptance Criteria

- [x] ~~A helper adds an entry to the named section of the [Unreleased] release, creating the subsection if it is absent, so a caller never positions text by hand.~~ ALREADY MET by `changelog.py compose`, which creates a missing section at the head of `[Unreleased]`. Verified in source, not assumed.
- [x] ~~The helper is idempotent enough to re-run: adding the same entry twice is refused or reported, never silently duplicated.~~ ALREADY MET: `compose` consumes the fragment, so idempotence is by consumption.
- [ ] A structural check fails when a release section's subsection headings are out of order, duplicated within one release, or when a subsection is empty - the shapes a bad hand-insert produces. This is the one criterion the filing got right and nothing covers.
- [ ] The structural check runs in the existing gate. Note the gate already binds `changelog-fragments` at a release cut (`gate.py`:1252); the structural check joins that lane rather than inventing one.
- [ ] While `changelog.d/` is live, a hand-edit of `CHANGELOG.md`'s `[Unreleased]` section is made visibly wrong rather than merely discouraged - the step that would have prevented both RUN-01KY3MFX incidents, and the one the original filing missed because it did not check whether the helper existed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | Darren Benson | Raised |
| 2026-07-22 | sdlc-studio | Corrected before refinement: the helper this CR says does not exist is `scripts/changelog.py`. Two of four ACs struck as already met, two added for the real gap. `Affects` re-pointed from `check_links.py` / `artifact.py` to `changelog.py` / `gate.py` via `transition.py annotate` - the original value named neither file this work touches. **The TITLE still asserts 'no helper' and is false.** It is left standing because a title lives in the filename, the H1 and the index row at once and no deterministic retitle path exists; correcting it by hand is the failure this CR is about. Filed as a friction point instead. |
