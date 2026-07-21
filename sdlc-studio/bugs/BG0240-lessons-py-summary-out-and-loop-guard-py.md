# BG0240: `lessons.py summary --out` and `loop_guard.py _state_path` write relative to the cwd, ignoring or failing to discover the root

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py,.claude/skills/sdlc-studio/scripts/loop_guard.py
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Two confirmed survivors of BG0228's exact shape, found by the sibling sweep that fix required (L-0154: a root-relative defect found in one writer must be swept across every sibling writer). Both were confirmed by RUNNING them from a foreign cwd, not by reading the code. lessons.py `cmd_summary` (lessons.py:1194) does `out_path` = Path(args.out) on a relative default, so --root is honoured for reads (BG0219 fixed `_project_file)` but not for this write. `loop_guard.py` `_state_path` (`loop_guard.py`:155-158) honours a NAMED --root but not the discovery half, so a default --root . resolves to the cwd. Both print a relative path that hides where the file went and exit 0, which is the third symptom BG0228 named.

## Steps to Reproduce

**lessons.py** - from a cwd that is not the project root, run:

```text
python3 lessons.py summary --root <proj> --out summary-out.md
```

Observed: prints `wrote 0 open lesson(s) -> summary-out.md`, exits 0, and the file lands beside
the cwd rather than under `<proj>`.

**loop_guard.py** - from `<proj>/scripts`, with the default `--root .`, run:

```text
python3 loop_guard.py record
```

Observed: writes a stray `<proj>/scripts/sdlc-studio/.local/loop-state.json` and reports
`continue (1 attempt(s), under guardrails)`, exit 0. A named `--root` is honoured, so this is the
discovery half of the defect rather than the ignore-the-root half.

Both were reproduced by running them, not by reading the code.

## Proposed Fix

Apply the same resolver BG0228 adopted rather than a third idiom: `verify_ac.resolve_root` for the root (a named root verbatim, the default '.' discovered upward) and `verify_ac.under_root` to anchor a relative --out, honouring an absolute path as given. Print the RESOLVED path, so a wrong destination is visible rather than hidden behind a relative string. Pin each from a cwd that is not the root - a test sharing one cwd lets two cwd-relative paths agree and both be wrong, which is why BG0228's own tests build and read from different directories.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
