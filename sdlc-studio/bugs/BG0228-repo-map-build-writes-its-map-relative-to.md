# BG0228: repo_map build writes its map relative to the current directory and ignores --root, then prints a relative path that hides where it went

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/repo_map.py
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Same defect class as BG0219 (lessons.py) and BG0220 (`verify_ac.py)`, found by BG0220's sibling-writer sweep and left unfixed as out of scope. `repo_map.py`:461 does out = Path(args.out) in `cmd_build` - a WRITE - with the relative default sdlc-studio/.local/repo-map.json, while --root is resolved at line 451 and never applied to it. The read side has the same hole at `repo_map.py`:472 and :514 (`map_path` = Path(args.map)), so build and query/stats disagree about where the map lives. The printed path is relative, so the output does not reveal that the file landed beside the cwd rather than under the named root.

## Steps to Reproduce

cd /elsewhere && `repo_map.py` build --root /proj. Observed: 'indexed 0 files -> sdlc-studio/.local/repo-map.json', written to /elsewhere/sdlc-studio/.local/repo-map.json, while /proj/sdlc-studio/.local does not exist. Expected: written under /proj, and the printed path absolute enough to show where.

## Proposed Fix

Route every path surface through the root resolver `verify_ac.py` now uses (`discover_root` plus a resolver that honours a named root verbatim and discovers only on the family default '.'), rather than adding a second path-joining idiom. Apply it to `cmd_build`'s --out and to the --map reads at :472 and :514 so build and query agree by construction. Print the resolved path, not the relative one.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Filed |
