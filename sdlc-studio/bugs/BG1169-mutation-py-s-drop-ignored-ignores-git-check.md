# BG1169: mutation.py's _drop_ignored ignores git check-ignore's exit code, so one path git refuses leaves the rest partly filtered

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, changelog.d/BG1169.md
> **Evidence:** BG1166 builder report, 2026-11-01. mutation.py `_drop_ignored`: `r = subprocess.run(["git", "-C", str(root), "check-ignore", "--stdin"], ...)` with no returncode check.
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T09:07:44Z

## Summary

Found by BG1166's builder (2026-11-01). `_drop_ignored` (.claude/skills/sdlc-studio/scripts/mutation.py, around line 1667) pipes candidate paths to `git check-ignore --stdin`, reads stdout and never checks the return code. git stops with rc 128 at a path beyond a symbolic link ('fatal: pathspec ... is beyond a symbolic link'). The gate host makes `sdlc-studio/.local` one (tools/remote-gate.sh:241). Every later path then comes back unfiltered, so the result is partly filtered. Its docstring says it returns the paths unfiltered on any git failure. No caller has yet been shown to pass a `.local` path.

## Steps to Reproduce

1. In a throwaway clone, `ln -s <dir> sdlc-studio/.local`.
2. Call `mutation._drop_ignored(root, [an ignored path, a path under sdlc-studio/.local, another ignored path])`.
3. The third path comes back even though git ignores it.

## Proposed Fix

Check the return code. On a fatal answer, either return the paths unfiltered as the docstring says, or drop the refused path and re-ask for the rest.

## Acceptance Criteria

- [ ] **AC1** `_drop_ignored` returns either every path unfiltered or a correctly filtered list when one input path lies beyond a symbolic link, never a partly filtered one.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py

## Impact

A mutation scan on a host with a symlinked ignored directory can scan ignored worktree copies of the tests, contrary to the function's own contract.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
