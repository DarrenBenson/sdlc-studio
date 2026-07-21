# BG0240: `lessons.py summary --out` and `loop_guard.py _state_path` write relative to the cwd, ignoring or failing to discover the root

> **Status:** Fixed
> **Verification depth:** functional - both were reproduced by RUNNING them from a foreign cwd before any edit, giving the filed symptoms verbatim, and re-run afterwards to see the file land under the resolved root; 13 of 18 new tests were RED first, every one run from a cwd that is not the root, with the write and the read in DIFFERENT directories; 14 hand-mutants applied, all killed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py,.claude/skills/sdlc-studio/scripts/loop_guard.py
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Two confirmed survivors of BG0228's exact shape, found by the sibling sweep that fix required (L-0154: a root-relative defect found in one writer must be swept across every sibling writer). Both were confirmed by RUNNING them from a foreign cwd, not by reading the code. lessons.py `cmd_summary` (lessons.py:1194) does `out_path` = Path(args.out) on a relative default, so --root is honoured for reads (BG0219 fixed `_project_file)` but not for this write. `loop_guard.py` `_state_path` (`loop_guard.py`:155-158) honours a NAMED --root but not the discovery half, so a default --root . resolves to the cwd. Both print a relative path that hides where the file went and exit 0, which is the third symptom BG0228 named.

## Acceptance Criteria

- [x] **AC1:** Run from a cwd that is NOT the project root, `lessons.py summary --root <proj> --out <rel>` writes under the resolved root and prints the RESOLVED path, leaving nothing beside the cwd.
      **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_lessons.py
- [x] **AC2:** Run from a subdirectory with the default `--root .`, `loop_guard.py record` discovers the project root upward instead of writing a stray workspace beside the cwd, and every verdict names the state file it used.
      **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_loop_guard.py
- [x] **AC3:** The read half and the write half resolve to the SAME root, so anchoring the write cannot leave the read pointing elsewhere. Pinned by tests that write from one directory and read from another.
      **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_loop_guard.py

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

## Resolution

Reproduced first, from a foreign cwd, exactly as filed. `lessons.py summary --root <proj>
--out summary-out.md` printed `wrote 0 open lesson(s) -> summary-out.md`, exited 0, and left
the file beside the cwd. `loop_guard.py record` from `<proj>/sub` wrote
`<proj>/sub/sdlc-studio/.local/loop-state.json` and printed a verdict naming no path at all.

Both now anchor on the resolver `repo_map.py` adopted, imported from `verify_ac` rather than
grown as a third idiom: `resolve_root` (a root the caller NAMED is honoured verbatim; the
family default `.` is discovered upward) and `under_root` (a relative output anchors on that
root, an absolute one is honoured as given). Each script gained one `_root(args)` so a single
invocation has ONE answer to which project it is working on - two idioms in one file is how a
writer and its reader come to disagree.

- `lessons.py`: `_project_file` resolves the root instead of taking `--root` verbatim, and
  `cmd_summary` anchors a relative `--out` on the SAME root the log was read from. Anchoring
  only the write would have let the digest and its source come from two different projects.
- `loop_guard.py`: `_state_path` anchors both the default state file and a relative
  `--state`. Every verdict now prints the resolved path (`[state: ...]`) - it printed no
  path at all, so a state file in the wrong tree looked exactly like one in the right tree.
  `record`'s and `status`'s JSON gained a `state` key for the same reason.

A THIRD symptom of the same defect was found in `loop_guard.py` while fixing the filed one,
in the same file and therefore fixed with it: `cmd_budget` read its run state from
`Path(args.root)` too, so from a subdirectory the appetite breaker found no run state, said
`no appetite declared - run is unbounded` and exited 0. A spent ceiling read as `continue`.
Demonstrated before and after against a run state carrying a spent appetite: exit 0 from the
subdirectory before, exit 4 (BUDGET_EXIT) after, matching what the run's own root reports.
Left unfixed it would have been WORSE than before this change, since `record` would have
written under the discovered root while `budget` read from the cwd.

Pinned by `SummaryOutRootAnchoringTests` in `tests/test_lessons.py` (8 cases) and
`RootAnchoringTests` in `tests/test_loop_guard.py` (10 cases). Every case runs from a cwd
that is NOT the root: a test that chdir'd to the root passes on a script ignoring `--root`
completely and proves nothing. The write/read pairs deliberately use different directories
and different root spellings - `record` from inside the project on the default root, `status`
from outside it on a named one; `summary` from a subdirectory, the digest read back from
elsewhere - because two equally cwd-relative paths agree with each other while both are
wrong. 13 of the 18 were RED before the fix.

Mutation-proven by hand (bytecode purged, `python3 -B`, each patch asserted to have changed
the file on disk), 14 mutants, all killed: the default state path back to a raw `--root`;
`--state` back to cwd-relative; each resolver reverted whole; `budget`'s root back to a raw
`--root`; the resolved path dropped from the continue line and from the quarantine line
separately; an absolute `--state` and an absolute `--out` each re-captured under the root;
`--out` back to cwd-relative; the lessons READ half reverted while the write stayed anchored;
a named root re-pointed by discovery in each script; the dry-run guard removed.

The sibling sweep the fix owes (L-0154) is reported, not fixed: 20 further scripts still
resolve the CLI `--root` as `Path(args.root)` with no discovery, 10 of them driving writes.
That is CR0383's scope, not this bug's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
| 2026-07-21 | claude | Fixed - both writers anchored on the shared family resolver and printing the resolved path; the `budget` breaker's silent unbounded verdict from a subdirectory found and fixed with them; 18 tests, 13 RED first, 14 mutants all killed |
