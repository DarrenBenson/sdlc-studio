# BG0228: repo_map build writes its map relative to the current directory and ignores --root, then prints a relative path that hides where it went

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/repo_map.py
> **Verification depth:** functional (red-then-green: 6 of 8 new tests failed on the unfixed script, each run from a cwd that is not the root; build/query/stats now agree by construction; 8 hand-mutants of the anchoring, the print and the discovery rule all killed)
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Same defect class as BG0219 (lessons.py) and BG0220 (`verify_ac.py)`, found by BG0220's sibling-writer sweep and left unfixed as out of scope. `repo_map.py`:461 does out = Path(args.out) in `cmd_build` - a WRITE - with the relative default sdlc-studio/.local/repo-map.json, while --root is resolved at line 451 and never applied to it. The read side has the same hole at `repo_map.py`:472 and :514 (`map_path` = Path(args.map)), so build and query/stats disagree about where the map lives. The printed path is relative, so the output does not reveal that the file landed beside the cwd rather than under the named root.

## Steps to Reproduce

cd /elsewhere && `repo_map.py` build --root /proj. Observed: 'indexed 0 files -> sdlc-studio/.local/repo-map.json', written to /elsewhere/sdlc-studio/.local/repo-map.json, while /proj/sdlc-studio/.local does not exist. Expected: written under /proj, and the printed path absolute enough to show where.

## Proposed Fix

Route every path surface through the root resolver `verify_ac.py` now uses (`discover_root` plus a resolver that honours a named root verbatim and discovers only on the family default '.'), rather than adding a second path-joining idiom. Apply it to `cmd_build`'s --out and to the --map reads at :472 and :514 so build and query agree by construction. Print the resolved path, not the relative one.

## Resolution

Reproduced first: from a foreign cwd, `build --root /proj` printed
`indexed 1 files in 0.00s -> sdlc-studio/.local/repo-map.json` and wrote it beside the cwd.

`repo_map.py` now imports the family resolver from `verify_ac` rather than growing a second
path-joining idiom: `resolve_root` (a root the caller NAMED is honoured verbatim; the family
default `.` is discovered upward instead of assumed to be the cwd) and `under_root` (a
relative `--out`/`--map` anchors on that root; an absolute one is honoured as given). Both
were private to `verify_ac`; they are public now, with a docstring saying why, and nothing
outside that module referenced the old names. Applied to `cmd_build`'s `--out` and to the
`--map` reads in `cmd_query` and `cmd_stats`, so build and query agree by construction. The
build line prints the resolved path, since a relative one cannot show whether the map landed
under the root or beside the cwd.

Pinned by `RootAnchoringTests` in `scripts/tests/test_repo_map.py`, 8 cases, every one run
from a cwd that is NOT the root (a test that chdir'd to the root would pass on a script that
ignores `--root` completely). The query and stats cases build and read from DIFFERENT
directories, or two equally cwd-relative paths would agree with each other and both be wrong.
6 of the 8 were red before the fix. Mutation-proven (bytecode purged, `python3 -B`), all
killed: `--out` back to cwd-relative; `--map` back to cwd-relative in query and in stats
separately; build's root back to `Path(args.root)`; an absolute `--out` re-captured under the
root; a named root re-pointed by discovery; discovery escaping a cwd with no project above it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Filed |
| 2026-07-21 | sdlc-studio | Fixed - build/query/stats anchor on the shared family resolver, resolved path printed; 8 mutation-proven tests |
