# US0307: A mutation or review window is declared on disk and skill scripts refuse or warn while it is open

> **Status:** Draft
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

### AC3: the gate reports an open window as a failing check, naming owner and paths

- **Given** a window open over named paths
- **When** `gate.py` runs
- **Then** the window check fails and its message names the owner and the claimed paths,
  so an author running the gate is told before committing rather than after
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::WindowCheckTests::test_an_open_window_fails_the_gate_naming_owner_and_paths
- **Verified:** yes (2026-07-22)

### AC4: with no window open, the gate result is unchanged

- **Given** no window record on disk, which is the normal state of every commit
- **When** `gate.py` runs
- **Then** the window check passes and no other check's verdict changes, so the guard
  cannot be disabled for being a nuisance on the common path
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::WindowCheckTests::test_no_window_leaves_the_gate_result_unchanged
- **Verified:** yes (2026-07-22)

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
