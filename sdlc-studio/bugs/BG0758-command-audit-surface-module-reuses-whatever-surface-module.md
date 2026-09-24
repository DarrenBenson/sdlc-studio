# BG0758: command_audit._surface_module reuses whatever surface module the process already imported

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/command_audit.py, .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py
> **Evidence:** US0895 review, RUN-01M39MC0: scratchpad u895r_leak.py and u895r_diag.jsonl
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`command_audit._surface_module` (`command_audit.py`:1072-1087) is documented to load the surface module of the skill tree it is judging, but it resolves any `surface` already in sys.modules. `test_docgen.py` puts scripts/lib on sys.path at import and caches `surface`, so any later in-process caller - the close checklist's doc-surface row, `sprint preflight` - judges a fixture tree with the dev repo's module and drops or misreads the doc-surface row. Reproduced under xdist (2 failed of 7303) and deterministically in one process after `import surface` (19 rows against 20). Same class as BG0559.

## Steps to Reproduce

1. In one Python process, `import surface` from the dev repo's scripts/lib. 2. Call sprint preflight's in-process checklist over a fixture skill tree with no scripts/lib. 3. The doc-surface row is missing; the CLI prints it as unreadable.

## Proposed Fix

Load the tree's own surface module by path under a unique module name, never through sys.modules, and report unreadable when the tree has none.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `command_audit._surface_module` (`command_audit.py`:1072-1087) is documented to load the surface module of the skill tree it is judging, but it resolves any...
- [ ] **AC2** The proposed fix lands, pinned by a test: Load the tree's own surface module by path under a unique module name, never through sys.modules, and report unreadable when the tree has none.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
