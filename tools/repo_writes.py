#!/usr/bin/env python3
"""Running the tests must leave the working tree exactly as it found it (BG0569).

Four instances in two days, three mechanisms, one shape: something that takes a root, or
defaults to one, writes where its author did not intend, and a real path looks exactly like a
temp path until somebody checks what changed. A fixture helper handed `.` as its root wrote
`src/thing.py`, a fake bug, and `sdlc-studio/.local/mutation-runs.json` into the real tree,
destroying 23 mutation registrations that `.local/` being gitignored made unrecoverable. A
rehearsal harness pointed its work root at the repository and one run wrote 41 fixture files
that `git add -A` swept onto main. A back-annotating batch run rewrote seven stories nobody had
touched. And a stray `sdlc-studio/bugs/BG0001-x.md` sat untracked until the duplicate-id lane
tripped over it. Every one was caught by a gate, none by its author.

Each was repaired at its own caller, and each repair is right. What was missing is a check on
the POPULATION - the suite, where roots are parameters - and the invariant is cheap to state:
running the tests must not modify a tracked file, create an untracked one, or touch
`sdlc-studio/.local/`. The last is the one that hurts, because it is gitignored and therefore
unrecoverable.

THIS IS THE GUARD, as a command line. `snapshot` records the tree; `check` compares it against
the tree now and names every path that moved. `.githooks/pre-commit` takes the snapshot at the
moment it SELECTS the unit suites, and `.githooks/commit-msg` runs the comparison once they have
finished - so the lane costs two directory reads and never a second suite run. It binds to the
suite RUN rather than to the push boundary for that reason: the cost the bug feared was a second
full suite, and wrapping the run that was going to happen anyway avoids it, while covering every
commit rather than every push. Its tests are `tools/tests/test_repo_writes.py`, which never
invokes a suite, so nothing here recurses.

THE TRAP THIS MUST NOT REPEAT. The guard test written the hour the fourth instance was found
asserted only over TOP-LEVEL entries, so it could not have seen `sdlc-studio/bugs/BG0001-x.md`
- the very file that prompted it. Both readings here are recursive by construction: `git status
--porcelain --untracked-files=all` reports one entry per FILE rather than per top directory,
and `.local/` is walked to its leaves.

WHAT IT DOES NOT WATCH, said plainly: ignored paths outside `sdlc-studio/.local/`. Listing every
ignored file would mean walking `node_modules/` and every agent worktree on each commit, and a
guard that costs that gets switched off.

Usage:
    python3 tools/repo_writes.py snapshot --root . --out FILE
    python3 tools/repo_writes.py check    --root . --since FILE

Exits 0 when the tree is unchanged, 1 when it moved (naming every path), 2 when the check
itself could not run - which is never read as "unchanged".
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

#: The gitignored runtime directory. Invisible to `git status`, so it is walked by hand - and
#: it is the half of the invariant that matters most, because nothing can restore it.
LOCAL_REL = "sdlc-studio/.local"

#: Directory names whose contents are machine artefacts of RUNNING python, not writes into the
#: tree. Purged and rebuilt constantly; a guard reporting them would report every run.
SKIP_DIRS = ("__pycache__", ".pytest_cache", ".mypy_cache")

#: The records the GATE ITSELF writes inside the comparison window, named one by one rather
#: than exempted with a wildcard on `.local/`. A wildcard would re-open exactly the hole this
#: guard exists to close: the mutation registrations that were destroyed live in the same
#: directory as these do.
#:
#: One exemption is NOT file-by-file - `HARNESS_DIRS` below - so "never by directory" would be
#: an overclaim. It is a prefix on one named subdirectory the harness owns outright, not on
#: `.local/`, and the state a stray write destroys does not live under it.
HARNESS_PATHS = (
    f"{LOCAL_REL}/gate-timings.json",        # tools/gate_timing.py record, between the lanes
    f"{LOCAL_REL}/gate-cost.json",           # gate.py's own cost series
    f"{LOCAL_REL}/gate-suite-last.log",      # commit-msg keeps a failing lane's output
    f"{LOCAL_REL}/gate-suite-verdict.json",  # gate.py --record-suite-verdict
    f"{LOCAL_REL}/suite-verdict.json",       # tools/run-suite.sh
)

#: Directories under `.local/` the harness owns wholesale (one file per run, pruned by age), and
#: the one place this guard exempts by PREFIX rather than by name. Enumerating them is not
#: possible: the filenames carry the run's own identity, so there is nothing to list in advance.
#: Kept to subdirectories the harness alone writes, never `.local/` itself.
HARNESS_DIRS = (f"{LOCAL_REL}/suite-logs",)

#: Git variables a hook inherits, pointing at the index of whatever invoked it. Dropped so both
#: halves of the comparison read the same repository the same way: the snapshot is taken from
#: `pre-commit` and the check from `commit-msg`, and a reading that changed with the ambient
#: environment between them would report a difference nobody made.
_GIT_ENV_VARS = (
    "GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_INDEX_VERSION",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE",
    "GIT_CEILING_DIRECTORIES", "GIT_DISCOVERY_ACROSS_FILESYSTEM", "GIT_PREFIX",
)


def _clean_env() -> dict:
    env = dict(os.environ)
    for var in _GIT_ENV_VARS:
        env.pop(var, None)
    return env


def _exempt(rel: str) -> bool:
    """True for a path the gate writes as part of running, so it is not evidence of a stray.

    Bytecode is exempt in BOTH readings, not only the `.local/` walk. The suites purge and
    rebuild `__pycache__` on every run - that is the repo's own defence against a cached `.pyc`
    serving a stale mutant - so a guard reporting it reddens on every commit, and a lane that
    reddens on every commit is one somebody switches off. It is exempted HERE rather than left
    to `.gitignore`, because a tree whose ignore rules do not cover it is exactly where the
    noise would appear.
    """
    parts = rel.split("/")
    if any(p in SKIP_DIRS for p in parts) or rel.endswith((".pyc", ".pyo")):
        return True
    if rel in HARNESS_PATHS:
        return True
    return any(rel == d or rel.startswith(d + "/") for d in HARNESS_DIRS)


def _stat_token(path: Path) -> str:
    """Size and modification time, so a file rewritten in place is a difference even when git
    already reported it as changed before the run."""
    try:
        st = path.stat()
    except OSError:
        return "gone"
    return f"{st.st_size}:{st.st_mtime_ns}"


def _git_status(root: Path) -> dict[str, str]:
    """Every path git reports as changed, one entry per FILE, as `<XY code>|<stat>`.

    `--untracked-files=all` is what makes this recursive: the default `normal` collapses an
    untracked directory to its top entry, which is the exact blindness the fourth instance
    slipped through. Ignored files are NOT listed - `.local/` is read separately below.
    """
    proc = subprocess.run(
        ["git", "-C", str(root), "-c", "core.quotepath=false",
         "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        capture_output=True, text=True, env=_clean_env())
    if proc.returncode != 0:
        raise RuntimeError(f"git status failed in {root}: {proc.stderr.strip()}")
    fields = proc.stdout.split("\0")
    out: dict[str, str] = {}
    i = 0
    while i < len(fields):
        entry = fields[i]
        i += 1
        if len(entry) < 4:
            continue
        code, rel = entry[:2], entry[3:]
        if code[0] in ("R", "C"):
            i += 1        # a rename/copy entry is followed by its source path
        if _exempt(rel):
            continue
        out[rel] = f"{code}|{_stat_token(root / rel)}"
    return out


def _local_state(root: Path) -> dict[str, str]:
    """Every file under `sdlc-studio/.local/`, to its leaves. Gitignored, so no git command
    reports it, and unrecoverable, so it is the half worth walking by hand."""
    base = root / LOCAL_REL
    out: dict[str, str] = {}
    if not base.is_dir():
        return out
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            rel = path.relative_to(root).as_posix()
            if _exempt(rel):
                continue
            out[rel] = _stat_token(path)
    return out


def snapshot(root: Path) -> dict:
    """The working tree as it stands: git's view, plus the gitignored runtime directory."""
    return {"root": str(root), "git": _git_status(root), "local": _local_state(root)}


def _git_verdict(code: str) -> str:
    """What git's own two-letter status says happened, so a report reads as English."""
    if "?" in code:
        return "created"
    if "D" in code:
        return "deleted"
    if "A" in code:
        return "added"
    return "modified"


def differences(before: dict, after: dict) -> list[tuple[str, str]]:
    """`(verdict, path)` for every path that moved. An empty list means the tree is unchanged.

    A path git stops reporting is `restored`: something wrote it and put it back. That is still
    reported, because a run that edits a tracked file and reverts it has raced every reader of
    that file, and silence about it is what made three of the four instances invisible.
    """
    found: list[tuple[str, str]] = []
    for rel in sorted(set(before.get("git", {})) | set(after.get("git", {}))):
        old, new = before.get("git", {}).get(rel), after.get("git", {}).get(rel)
        if old == new:
            continue
        found.append(("restored" if new is None else _git_verdict(new.split("|", 1)[0]), rel))
    for rel in sorted(set(before.get("local", {})) | set(after.get("local", {}))):
        old, new = before.get("local", {}).get(rel), after.get("local", {}).get(rel)
        if old == new:
            continue
        found.append(("created" if old is None else
                      "removed" if new is None else "modified", rel))
    return found


def report(found: list[tuple[str, str]]) -> str:
    """The refusal, self-diagnosing in this gate's convention: what moved, and where to look."""
    lines = [f"the test run changed {len(found)} path(s) in the working tree:"]
    for verdict, rel in found:
        note = "   (gitignored - nothing can restore it)" if rel.startswith(LOCAL_REL) else ""
        lines.append(f"  {verdict:<9} {rel}{note}")
    lines.append("")
    lines.append("TWO causes produce this, and the guard cannot tell them apart - its window is "
                 "the whole suite run, so anything that touched the tree in those minutes lands "
                 "here. Check the second one FIRST, because it is the likelier and the cheaper:")
    lines.append("")
    lines.append("  1. A fixture wrote into the repository, which is writing over real work. "
                 "Find the root it took: a helper that accepts a root and was handed `.`, a "
                 "harness whose work root is not under tempfile, or a batch verb run without "
                 "--dry-run.")
    lines.append("  2. YOU edited a tracked file while the gate was running. The suites take "
                 "minutes and the snapshot is taken before them, so an edit made meanwhile is "
                 "indistinguishable from a fixture write. If the paths above are ones you were "
                 "working on, this is that - re-run the commit without touching the tree.")
    lines.append("")
    lines.append("Telling them apart: `git diff` the named paths. Changes you recognise as your "
                 "own are cause 2; fixture debris - a `src/thing.py`, a fake artefact id, a "
                 "rewritten `.local/` record - is cause 1 and must be traced to its writer.")
    return "\n".join(lines)


def _cmd_snapshot(args) -> int:
    Path(args.out).write_text(json.dumps(snapshot(Path(args.root))), encoding="utf-8")
    return 0


def _cmd_check(args) -> int:
    since = Path(args.since)
    if not since.is_file():
        print(f"repo-writes: no snapshot at {since} - the tree BEFORE the run was never "
              f"recorded, so whether it moved is unknown. Refusing rather than assuming.",
              file=sys.stderr)
        return 2
    before = json.loads(since.read_text(encoding="utf-8"))
    found = differences(before, snapshot(Path(args.root)))
    if not found:
        return 0
    print("repo-writes: " + report(found))
    return 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="repo_writes.py",
        description="Refuse a test run that wrote into the working tree.")
    sub = parser.add_subparsers(dest="verb", required=True)
    snap = sub.add_parser("snapshot", help="record the tree before a run")
    snap.add_argument("--root", default=".")
    snap.add_argument("--out", required=True)
    snap.set_defaults(func=_cmd_snapshot)
    chk = sub.add_parser("check", help="compare the tree against a recorded snapshot")
    chk.add_argument("--root", default=".")
    chk.add_argument("--since", required=True)
    chk.set_defaults(func=_cmd_check)
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"repo-writes: the check could not run ({exc})", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
