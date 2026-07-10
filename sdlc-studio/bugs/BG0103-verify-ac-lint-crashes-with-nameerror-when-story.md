# BG0103: verify_ac lint crashes with NameError when --story is not passed

> **Status:** Fixed
> **Verification depth:** functional (red-then-green: NameError reproduced at HEAD, directory + single-story lint paths covered; critic re-ran the repro live and probed --story/--dir/--root dodges)
> **Severity:** Medium
> **Created:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

Found by a benchmark delivery agent dogfooding the v4 RC payload inside a fixture workspace: '`verify_ac.py` lint' (no --story) raises NameError at `cmd_lint` - the directory path is built with `_under_root(repo_root`, args.dir) but `repo_root` is only defined in `cmd_run`'s parser (--repo-root belongs to the run subcommand). Any lint over a stories directory crashes; the single-story path works. The load-bearing 'run' gate is unaffected.

## Steps to Reproduce

python3 scripts/`verify_ac.py` lint --dir sdlc-studio/stories -> NameError: name '`repo_root`' is not defined

## Proposed Fix

give the lint subparser its own --root (default .) and resolve `_under_root(Path(args.root)`, args.dir); regression test covers the no-story path

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Filed |
