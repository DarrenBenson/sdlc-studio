# Lessons Summary

Rolling digest of still-valid project lessons, read at sprint start. The full log with closed entries lives in the project tier (`.local/lessons.md`); regenerate this with `lessons summary`.

- **L-0005: Editing a shared template obliges you to run its renderer's tests**
- **L-0004: Add a closing full-diff pass when units share a file**
- **L-0003: Read every creation path, not the one the design note names**
- **L-0002: Forward-port via install.sh, not per-file cp** - Sync with `install.sh --local` (whole-tree, deterministic), then `diff -rq` to verify
- **L-0001: Amend the AC in the same unit when the implementation deviates** - When deviating, reword the AC + add a revision-history note in the same commit; the critic checks AC-vs-delivered-behaviour
