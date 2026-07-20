# BG0219: lessons summary ignores --root and writes relative to the current directory

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The summary subcommand derives its output path from --project-file, which defaults to the RELATIVE string sdlc-studio/.local/lessons.md, and --root is documented as read only for config keys. So lessons.py --root /somewhere summary reads and writes relative to the CURRENT DIRECTORY, ignoring the root it was given, and reports success naming the path it wrote. sprint close passes --root correctly and inherits the bug: a close run from anywhere other than the project root regenerates the digest in the wrong place and reports the lessons-summary step green. Found because a close run from the scripts directory during a test created a stray sdlc-studio/retros/LESSONS-SUMMARY.md inside scripts/ and it was committed. Root-aware helpers already exist - `default_project_file(repo_root)` and `default_summary_path(repo_root)` - and `summary_status` uses them, so the module already knows how to do this correctly in one place and not the other. It works from the repo root only by the coincidence that cwd equals root.

## Steps to Reproduce

1. From any directory that is not the project root, run lessons.py --root /path/to/project summary. 2. It writes sdlc-studio/retros/LESSONS-SUMMARY.md under the CURRENT directory, not under /path/to/project. 3. It prints wrote N open lesson(s) naming that wrong path and exits 0. 4. Equivalently: run the ClosePreflightTests class from the scripts directory and observe scripts/sdlc-studio/retros/LESSONS-SUMMARY.md appear.

## Proposed Fix

Resolve --project-file and the summary output against --root when the path is relative, using the existing `default_project_file` and `default_summary_path` helpers so there is one authority rather than two. Add a test that runs summary with --root pointing at a temp workspace from a different cwd and asserts the file lands under the root and nothing is written beside the cwd. Consider the same audit for other subcommands taking both --root and a defaulted relative path.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Filed |
