# US0307: A mutation or review window is declared on disk and skill scripts refuse or warn while it is open

> **Status:** Review
> **Delivers:** CR0388
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py,.claude/skills/sdlc-studio/scripts/gate.py,.claude/skills/sdlc-studio/scripts/tests/test_mutation.py,.claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Epic:** EP0103
> **Points:** 5

## User Story

**As an** author committing ceremony artefacts while an independent review works the
same tree
**I want** any process that rewrites source files in place to declare an open window on
disk
**So that** my commit is told a concurrent writer is active, instead of my discovering
it from an alarming diff after the fact

## Context

**Built against the corrected mechanism in CR0388, not its Summary.** The staged
`retro.py` at RUN-01KY321Q did **not** carry a hand-applied mutant. The reviewer had
built a helper directory with `ln -sf <repo>/scripts/*.py .` and then run
`git show <sha>:...retro.py > retro.py` inside it; the redirect followed the symlink and
overwrote the live working tree with the pre-sprint version, silently reverting two
units' work. The reviewer found it with `git status`, restored from HEAD and disclosed
it.

So the guard must not depend on the change being recognisable as a mutant, nor on the
suite going red. What survives, and is what this story builds, is that **a concurrent
process rewrote a source file in the author's tree and nothing announced it**. The
commit was blocked only because the reverted source failed the suite; a rewrite that
left the suite green would have been committed silently under a paperwork commit
message.

The single-writer rule already exists for `mutation.py` runs during a build. The window
record generalises it: any process rewriting files in place declares what it may touch,
for as long as it may touch it. The existing `mutation-inflight.json` sidecar is the
model - a file, so it survives the SIGKILL that in-memory state does not.

US0308 is the commit path that reads the window. This story is the record and the
readers inside the skill.

## Acceptance Criteria

### AC1: a window is a record on disk naming its owner, its start and its paths

- **Given** a run that rewrites source files in place, such as a `mutation.py` gate run
- **When** the window opens
- **Then** a record under `sdlc-studio/.local/` names the owner, the time it opened and
  the paths it may rewrite, and the record is cleared when the run finishes normally
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::WindowDeclarationTests::test_a_run_declares_a_window_naming_owner_and_paths_and_clears_it
- **Verified:** yes (2026-07-22)

### AC2: a window outlives the process that opened it

- **Given** a run killed mid-window with SIGKILL, so no handler and no `finally` runs
- **When** the next reader looks
- **Then** the window is still reported open, with its owner and the command that clears
  it, rather than being read as absent - an unreadable or truncated record is likewise
  reported open, never as closed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::WindowDeclarationTests::test_a_window_left_by_a_killed_run_is_still_reported_open
- **Verified:** yes (2026-07-22)

### AC3: the gate reports an open window, and FAILS when it claims a staged path

- **Given** a window open over named paths
- **When** `gate.py` runs
- **Then** the window check reports the open window with its owner and the claimed paths, so
  an author running the gate is told before committing rather than after; it FAILS when the
  window claims a path this commit has staged, and passes when it does not, so a reviewer
  holding a window scopes staging rather than freezing the tree
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::WindowCheckTests::test_an_open_window_fails_the_gate_naming_owner_and_paths
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::WindowLaneIsPathScopedTests
- **Verified:** yes (2026-07-22)

### AC4: with no window open, the gate result is unchanged

- **Given** no window record on disk, which is the normal state of every commit
- **When** `gate.py` runs
- **Then** the window check passes and no other check's verdict changes, so the guard
  cannot be disabled for being a nuisance on the common path
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::WindowCheckTests::test_no_window_leaves_the_gate_result_unchanged
- **Verified:** yes (2026-07-22)

## The record contract, as READ by this module

The published contract (see US0308) names two spellings, and this module now honours both:

- `sdlc-studio/.local/*window*.json`, or `sdlc-studio/.local/windows/*.json`
- `mutation.window_records` is the ONE discovery. `read_window` / `read_windows` /
  `open_window` / `close_window` and the gate's `window` lane all go through it, and
  `close_window` unlinks the record it actually read rather than a fixed filename.
- Claimed paths are normalised to repo-relative at OPEN time (`window_claim`), because the
  readers compare them against repo-relative `git diff --cached --name-only`. A path outside
  the root is left verbatim, where both readers treat it as uninterpretable and so claiming
  the whole tree.

## Repair round (independent review of RUN-01KY3MFX)

Three findings, all reproduced first and all now pinned:

1. **The gate lane was PATH-BLIND and blocking**, so while any window was open no commit could
   land whatever it staged - contradicting the hook, which in the same run printed "No staged
   path is claimed by it, so this commit proceeds". The lane now judges the staged paths. AC3
   above is rewritten to what the code does; the contradiction is pinned by
   `test_gate.WindowLaneIsPathScopedTests` and by
   `test_precommit_window_guard.WindowGuardTests.test_the_gate_lane_does_not_contradict_the_guard_in_the_same_run`.
2. **`read_window` honoured one spelling of the two**, so a record at `.local/windows/*.json`
   was reported "no rewrite window is open" while blocking commits, and `window open` let a
   second writer in. Fixed by `window_records`; pinned by
   `test_mutation.WindowRecordContractTests` and by the cross-reader agreement tests in
   `test_precommit_window_guard.OneRecordContractTests`.
3. **`open_window` stored claims verbatim**, so any absolute `--root` (which is what
   `select_files` produces) wrote claims no reader could match: the window announced a rewrite
   and the commit rewriting that exact file landed. Fixed by `window_claim`.

## Open Questions

- CR0388 says the commit path "refuses **or** warns" and does not settle which. AC3 is
  written as a refusal, because the request's own final criterion asks for a test that
  "asserts the commit is refused". If warn-only is wanted for the gate while the hook
  refuses, AC3 changes.
- The request names the commit path only. Whether other skill scripts that write to the
  tree (`reconcile.py apply`, `artifact.py`, `transition.py`) must also refuse while a
  window is open is unspecified, and is not covered here.
- How a human reviewer opens a window is unspecified. `mutation.py` can declare one for
  itself; a reviewer hand-editing files needs a command to open and close one, and
  CR0388 does not name it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Repair round: gate lane made path-scoped, one reader over both record spellings, claims normalised at open time; 15 hand-applied mutants, all killed |
