# BG0282: 59 scripts still resolve --root bare, so a run from a subdirectory reads or writes the wrong tree

> **Status:** Open
> **Severity:** Medium
> **Points:** 13
> **Affects:** .claude/skills/sdlc-studio/scripts/, sdlc-studio/reviews/root-census.md
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The root census measured every shipped script in the family: 5 anchored, 59 unanchored, 5 with no --root surface at all. An unanchored script takes the family default '.' as the cwd instead of discovering the workspace above it, so a run from a subdirectory silently operates on a tree that is not the project. 26 of the 59 write, which is the fail-open case: the output lands in a stray sdlc-studio/ tree beside the cwd, the path used is printed, the exit code is 0, and the gate that reads the file never sees it. The remaining 33 read, which returns an answer about a workspace nobody asked about. The allocator was fixed first because it is the collision case. This bug tracks the rest.

## Steps to Reproduce

1. Pick any script listed unanchored in sdlc-studio/reviews/root-census.md.
2. cd into a subdirectory of the project, for example .claude/skills/sdlc-studio/scripts/.
3. Run the script with no --root.
4. Observe it operate on the cwd rather than on the workspace above it - a reader answers about an empty tree, a writer creates one.

## Proposed Fix

Replace the bare Path(args.root) with `sdlc_md.resolve_root(args)`, and anchor every relative output path with `sdlc_md.under_root(root`, rel). Deliver in slices rather than one sweep: the 26 writers first, then the readers. Update sdlc-studio/reviews/root-census.md as each script moves to anchored - the census guard holds the record to the measurement, so the record cannot claim an anchor a script does not have.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Filed |
