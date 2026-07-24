# BG0288: anchor the 33 unanchored READER scripts to the discovered root (BG0282 slice 2)

> **Status:** Fixed
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/, sdlc-studio/reviews/root-census.md
> **Verification depth:** functional (same contract suite, readers half; the applicable set is measured from the family, never listed, so a script cannot escape by being forgotten)
> **Severity:** Medium
> **Points:** 5

## Summary

Slice 2 of [[BG0282]]: the reader half of the same defect. A script that takes the family
default `--root .` as the cwd, rather than discovering the workspace above it, returns an
answer about a tree nobody asked about. Run `status`, `gate`, `audit` or `flow` from a
subdirectory and they report on an empty project - clean, confident and irrelevant - with exit
code 0. That is quieter than the writer case but not safer: a gate that finds nothing to fail
reads exactly like a gate that passed.

The count in the title is the figure measured when [[BG0282]] was filed. It had already moved
by the time this slice ran: a parallel branch anchored five more scripts, so the measurement at
delivery was 28 writers and 26 readers out of 54. The census records the measurement, not the
title.

## Steps to Reproduce

1. Pick any script recorded unanchored in `sdlc-studio/reviews/root-census.md`.
2. `cd` into a subdirectory of the project, for example `.claude/skills/sdlc-studio/scripts/`.
3. Run the script with no `--root`.
4. Observe it report on the cwd rather than on the workspace above it - an empty tree, and an
   exit code that says all is well.

## Proposed Fix

The same repair as slice 1, applied to the readers: resolve the root ONCE in `main()` with
`sdlc_md.resolve_root(args)` and write it back onto `args`, so every verb below receives the
discovered root instead of a bare `.`. Anchor any relative output path with
`sdlc_md.under_root(root, rel)`. Update `sdlc-studio/reviews/root-census.md` as each script
moves.

## Acceptance Criteria

### AC1: every reader script anchors its root on the discovered project before it dispatches

- **Given** a script that declares `--root` and does not mutate a tree, run with the family
  default from a subdirectory of a project
- **When** its `main()` reaches the dispatch
- **Then** the value the verb receives is the DISCOVERED project root, not the cwd
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_root_anchor_contract.RootAnchorContractTests.test_every_reader_script_anchors_its_root_before_dispatch
- **Verified:** yes (2026-07-24)

### AC2: no script in the family is left unanchored by the measurement

- **Given** the census guard's own measurement of every shipped script
- **When** it classifies the family
- **Then** no script that declares `--root` is left recorded unanchored without the reason
  naming why the measurement cannot see its anchor
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_root_census.RootCensusTests.test_an_unanchored_entry_needs_a_fix_or_a_filed_follow_up
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed from the skeleton and delivered |
