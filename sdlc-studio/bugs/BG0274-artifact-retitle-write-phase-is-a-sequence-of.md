# BG0274: artifact.retitle write phase is a sequence of independent writes with no rollback, so a fault mid-loop (e.g. an unreadable reference file) leaves the file renamed and index updated but inbound references half-rewritten

> **Status:** Open
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_retitle_refs.py
> **Severity:** Medium
> **Points:** 5

## Summary

`artifact.retitle` documents itself as all-validate-then-write, and that guarantee holds only
on the REFUSAL path. Once the four surfaces validate, the write phase is a sequence of
independent writes with no journal and no rollback: the destination file, the unlink of the
old name, the index row, then one rewrite per inbound reference in a loop. Anything raising
partway through - an unreadable reference file, a full disk, a permission change under the
tree, a kill - leaves the artefact renamed, the index updated and the references half
rewritten. That is precisely the split-surface state the validate-first discipline exists to
prevent, and it is silent: the caller sees an exception and has no way to tell how far the
write got.

## Steps to Reproduce

1. Take an artefact with two or more inbound references and an index row.
2. Make the second reference file unwritable (or otherwise fail its write).
3. Run `artifact.py retitle --id <ID> --title "<new>"`.
4. Observe: the artefact file is renamed to the new slug with the new H1, the index row points
   at the new filename, the FIRST reference is rewritten, and the second is not - four surfaces
   in three different states, with no report of which.

## Proposed Fix

Journal the prior bytes of every file the write phase will touch (the source path, the
destination, the index and each rewritable reference) before the first write, and restore them
all if any single write raises. A file that did not exist before is removed rather than
restored, so a created-then-abandoned destination is not left behind either. The fault is then
reported as a `RetitleBlocked` on a `write` surface, chained to the original error, so the
caller learns which write failed and that the tree was put back. A rollback that cannot itself
restore a surface names that surface instead of claiming a clean one.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed: symptom, repro, fix and executable ACs authored |
| 2026-07-24 | sdlc | Fixed: write phase journalled - atomic-or-rolled-back, partial rollback reported honestly |

## Acceptance Criteria

- [ ] AC1: a fault mid-write leaves every surface byte-identical to before the retitle
- **Given** an artefact with two inbound references and an index row, whose SECOND reference write fails
- **When** `retitle` runs
- **Then** the artefact keeps its old filename and bytes, the destination filename does not exist, the index row is unchanged, and the reference already rewritten is restored
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retitle_refs.py::RetitleRollbackTests::test_a_fault_mid_write_leaves_every_surface_byte_identical

- [ ] AC2: the fault is reported, never swallowed, and the CLI exits non-zero
- **Given** the same failing write
- **When** `retitle` runs, and separately when `artifact.py retitle` is invoked
- **Then** a `RetitleBlocked` on the `write` surface names the path whose write failed and states that the tree was rolled back, the original error is chained to it, and the command exits non-zero having written nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retitle_refs.py::RetitleRollbackTests::test_the_fault_is_reported_and_the_cli_exits_non_zero

- [ ] AC3: a rollback that cannot restore a surface names it rather than claiming a clean one
- **Given** a write fault whose rollback also fails for one file
- **When** `retitle` runs
- **Then** the raised message names that file as unrestored and does not claim the tree was put back - a partial rollback reported as a clean one is worse than the original fault
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retitle_refs.py::RetitleRollbackTests::test_a_failed_rollback_names_what_it_could_not_restore
