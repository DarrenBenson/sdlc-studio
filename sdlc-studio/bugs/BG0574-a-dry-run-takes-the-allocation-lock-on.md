# BG0574: A --dry-run takes the allocation lock on the target repository, so a preview writes into the tree it was asked only to describe

> **Status:** Open
> **Created:** 2026-08-11
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Severity:** Medium
> **Points:** 2

## Summary

Found by the new repo-writes lane refusing a commit, then traced by instrumenting the lock rather than by reading. `artifact.py new` opens `sdlc-studio/.local/allocation.lock` for writing at artifact.py:1083 and only tests `dry_run` at 1102 and 1108. So the preview path - whose entire contract is that it writes nothing - creates or truncates a file in the target repository before it decides not to write anything else.

The reason this surfaced now is the sharper half. `test_file_finding.py` sets `_ROOT = Path(__file__).resolve().parents[5]`, which is the LIVE repository, and drives `artifact.py new --root <live repo> ... --dry-run` as a subprocess. Reading the real corpus is legitimate there: the criterion is about a selector naming a real test file, and the invocation needs a real epic. Writing to it is not, and the only thing standing between that test and minting artefacts into the working repository is a single flag.

Nothing was lost. No artefact was minted, and the file is a zero-byte advisory lock. What is wrong is the shape: a preview that writes, and a test whose work root is the repository it is running inside.

> **Verification depth:** functional (unit: the whole-tree assertion over a preview, with the
> lock-taken-unconditionally mutant measured against it)

## Acceptance Criteria

### AC1

- **Given** `artifact.py new` invoked with `dry_run=True` against a repository
- **When** it returns its preview
- **Then** NOTHING has been created anywhere under that repository, asserted over the whole tree
  rather than over the lock alone, so the next thing a preview starts writing fails here too
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py -k dry_run_writes_NOTHING
- **Mutant:** take `sdlc_md.allocation_lock(root)` unconditionally again, as it was.

## Steps to Reproduce

1. `stat -c %Y sdlc-studio/.local/allocation.lock`. 2. `python3 -B -m pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py -q`. 3. `stat` again - the mtime has moved. Instrumenting `sdlc_md.allocation_lock` to dump a stack when its root resolves to the live repository names `artifact.py main -> cmd_new -> new -> allocation_lock`, reached through a subprocess the test spawns.

## Proposed Fix

Two parts. In `artifact.py new`, hoist the `dry_run` decision above `with sdlc_md.allocation_lock(root)`, or make the lock a no-op under `dry_run`. A preview needs no serialisation because it mints nothing: the lock exists to stop two writers minting the same id, and a dry run is not a writer.

In the test, stop pointing a write verb at the repository it runs inside. If the real corpus is genuinely needed for the selector to resolve, read it and construct the artefact against a temp root, or copy the two files the criterion needs into a fixture. `--dry-run` is a flag, and a guard that depends on a flag nobody may remove is not a guard.

## Impact

Today, a touched lock file and a refused commit, because the repo-writes lane correctly reports it. The exposure is that the same test is one edit away from minting artefacts into a working repository, and it is a test whose whole subject is writers that take a root. Medium: no data is lost, the behaviour is deterministic, and the lane that caught it is now in place.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-11 | sdlc-studio | Created via `new` (deterministic) |
