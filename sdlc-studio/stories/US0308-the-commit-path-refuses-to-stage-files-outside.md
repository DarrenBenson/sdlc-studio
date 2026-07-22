# US0308: The commit path refuses to stage files outside the declared change set while a window is open

> **Status:** Draft
> **Delivers:** CR0388
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .githooks/pre-commit,tools/tests/test_precommit_window_guard.py
> **Epic:** EP0103
> **Points:** 3

## User Story

**As an** author making a paperwork commit during a closing review
**I want** the pre-commit hook to refuse a staged path that an open window claims
**So that** a `git add -A` cannot commit whatever state a concurrent process has left in
a source file, in the case where the suite stays green and nothing else would notice

## Context

**Written against the corrected mechanism in CR0388, not its Summary.** The file staged
at RUN-01KY321Q was not a mutant: a reviewer's `ln -sf` helper directory turned a
`git show <sha>:... > retro.py` redirect into a write through the symlink into the live
tree, reverting two units' work. The hook must therefore not try to recognise a mutant,
and must not rely on the suite going red. The commit was refused only because the
reverted source failed the suite; a rewrite leaving the suite green would have been
committed silently under a commit message about paperwork.

The rule this story builds is the one that catches the incident without needing to know
how the file came to be wrong: **while a window is open, a staged path the window claims
is refused, however green everything else is.** US0307 delivers the window record; this
is the reader in `.githooks/pre-commit`.

AC1 is the case the existing gate cannot catch today, and is the one that must not be
weakened into "the suite went red".

## Acceptance Criteria

### AC1: green is not enough - a staged path an open window claims is refused

- **Given** a window open over a named source file, that file altered in the working
  tree by the concurrent process, and every other gate lane including the unit suites
  green
- **When** a commit stages it, whether by `git add -A` or by naming it
- **Then** the hook refuses and its message names the open window and the offending
  staged path
- **Verify:** pytest tools/tests/test_precommit_window_guard.py::WindowGuardTests::test_a_green_staged_path_claimed_by_an_open_window_is_refused
- **Verified:** yes (2026-07-22)

### AC2: scoped staging still commits while a window is open

- **Given** the same open window
- **When** the commit stages only paths the window does not claim, which is the shape of
  every ceremony commit during a review
- **Then** the hook proceeds normally, so the guard scopes staging rather than freezing
  the tree for the duration of a review
- **Verify:** pytest tools/tests/test_precommit_window_guard.py::WindowGuardTests::test_staging_only_unclaimed_paths_proceeds_while_a_window_is_open
- **Verified:** yes (2026-07-22)

### AC3: the refusal names the way forward

- **Given** the refusal in AC1
- **When** its message is printed
- **Then** it names the scoped-staging path (commit the named paths rather than
  `git add -A`) and how to clear a window left open by a killed process, per the hook's
  self-diagnosing convention
- **Verify:** pytest tools/tests/test_precommit_window_guard.py::WindowGuardTests::test_the_refusal_names_the_scoped_staging_remedy
- **Verified:** yes (2026-07-22)

### AC4: with no window open, the hook behaves as before

- **Given** no window record on disk
- **When** any commit is made, including one that stages the same file AC1 refused
- **Then** the hook's verdict, lane selection and output are unchanged from before this
  story, so the normal path pays nothing
- **Verify:** pytest tools/tests/test_precommit_window_guard.py::WindowGuardTests::test_no_window_open_leaves_the_hook_behaviour_unchanged
- **Verified:** yes (2026-07-22)

## The record contract this reader implements

US0307 writes the window; this story reads it. The reader in `.githooks/pre-commit` accepts
either spelling, so a writer choosing one file or one file per window both work:

- `sdlc-studio/.local/*window*.json`, or `sdlc-studio/.local/windows/*.json`
- `{"owner": "who holds it", "opened": "<iso8601>", "paths": ["a/file.py", "dir/", "glob*"]}`
- A path claim matches the file itself, anything beneath it when it names a directory, or a
  glob. `/` and `.` claim the whole tree.
- Three readings fail SAFE, each with its own test: an unreadable or truncated record, a
  record that is not a JSON object, and a record naming no paths are all read as an OPEN
  window claiming everything. A half-written record must never read as "closed".
- No record on disk means no window: the guard prints nothing and costs nothing (AC4).

## Open Questions

- CR0388 does not say how the author declares their own change set. The title reads
  "outside the declared change set", which could mean a set the author declares; the ACs
  above are written against the paths the **window** claims, because that is the set
  that exists on disk and it catches the observed incident. If the author is to declare
  a set explicitly, the mechanism (flag, environment variable, file) is unspecified.
- CR0388's third criterion asks that `reference-sprint.md` state the hazard where it
  states the single-writer rule for mutation runs. That criterion is now carried by
  US0310 (EP0105), which was minted after this story was written.
- The refusal tells an author to delete a stale record by path, because that is a
  statement this story can stand behind: the record is a file. It deliberately does NOT
  name a `window close` command, since none exists until US0307 ships one; naming a
  command that does not exist would be the same class of defect as the guard itself
  exists to catch.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Built red-first against the corrected mechanism; record contract recorded; 14 mutants applied, 4 findings from the survivors (three dead clauses removed, one fail-open claim shape fixed) |
