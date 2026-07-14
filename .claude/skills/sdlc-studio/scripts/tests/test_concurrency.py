"""US0069/CR0183: passive concurrency safety - atomic index writes and an advisory
allocation lock, so the ledger stays safe under concurrent writers.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import ast
import importlib.util
import re
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))
from lib import sdlc_md  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


artifact = _load("artifact")
reconcile = _load("reconcile")


def _index(repo: Path, type_: str, header: str) -> None:
    d = repo / sdlc_md.ARTIFACT_TYPES[type_][0]
    d.mkdir(parents=True, exist_ok=True)
    ncols = header.count("|") - 1
    sep = "| " + " | ".join(["---"] * ncols) + " |"
    (d / "_index.md").write_text(
        "# Index\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Open | 0 |\n"
        "| **Total** | **0** |\n\n## All\n\n" + header + "\n" + sep + "\n", encoding="utf-8")


class AtomicWriteTests(unittest.TestCase):
    def test_atomic_write_leaves_original_intact_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "f.txt"
            p.write_text("original", encoding="utf-8")
            with mock.patch("os.fdopen", side_effect=RuntimeError("boom")):
                with self.assertRaises(RuntimeError):
                    sdlc_md.atomic_write(p, "clobbered")
            self.assertEqual(p.read_text(encoding="utf-8"), "original")  # not truncated
            self.assertEqual(list(Path(d).glob(".tmp-*")), [])           # no temp left behind

    def test_atomic_write_replaces_content(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "f.txt"
            sdlc_md.atomic_write(p, "hello")
            self.assertEqual(p.read_text(encoding="utf-8"), "hello")

    def test_atomic_write_preserves_mode(self) -> None:
        # CR0207: mkstemp makes 0600 and os.replace keeps it - atomic_write must restore the
        # existing file's mode, else every rewrite silently flips it to owner-only.
        import os
        import stat
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "f.txt"
            p.write_text("x", encoding="utf-8")
            os.chmod(p, 0o664)
            sdlc_md.atomic_write(p, "y")
            self.assertEqual(stat.S_IMODE(os.stat(p).st_mode), 0o664)


# --------------------------------------------------------------------------------------
# Source guard: every live `_index.md` write goes through sdlc_md.atomic_write.
#
# atomic_write is the module's own torn-write guard, and a guard applied on only some of
# the paths is not a guard: one plain `Path.write_text` on an index reopens the whole
# corruption window for every reader. This scans the shipped scripts rather than pinning
# the three writers that were once wrong, so a NEW offender fails the suite too.
# --------------------------------------------------------------------------------------

# an identifier that names an index path: idx, index, index_path, live_idx, story_index ...
_INDEX_NAME_RE = re.compile(r"(?:^|_)(?:idx|index)(?:$|_)")
_INDEX_LITERAL = "_index.md"


def _index_named(expr: str) -> bool:
    """True when a receiver expression is an index path by name or by literal."""
    if _INDEX_LITERAL in expr:
        return True
    return any(_INDEX_NAME_RE.search(part) for part in re.split(r"\W+", expr.lower()) if part)


def _index_bound_names(tree: ast.AST) -> set[str]:
    """Names bound anywhere in the module to an expression that builds an `_index.md` path,
    so a writer whose variable is not conventionally named is still caught."""
    bound: set[str] = set()
    for node in ast.walk(tree):
        targets = []
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, value = [node.target], node.value
        else:
            continue
        if _INDEX_LITERAL not in ast.unparse(value):
            continue
        for t in targets:
            if isinstance(t, ast.Name):
                bound.add(t.id)
    return bound


def _non_atomic_index_writes(path: Path) -> list[str]:
    """`file:line` for every `<index>.write_text(...)` / `open(<index>, 'w')` in one script."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    bound = _index_bound_names(tree)
    offenders: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        recv = None
        if isinstance(node.func, ast.Attribute) and node.func.attr == "write_text":
            recv = ast.unparse(node.func.value)
        elif isinstance(node.func, ast.Name) and node.func.id == "open" and node.args:
            mode = node.args[1] if len(node.args) > 1 else None
            written = isinstance(mode, ast.Constant) and "w" in str(mode.value)
            written = written or any(k.arg == "mode" and isinstance(k.value, ast.Constant)
                                     and "w" in str(k.value.value) for k in node.keywords)
            if written:
                recv = ast.unparse(node.args[0])
        if recv is None:
            continue
        if _index_named(recv) or recv in bound:
            offenders.append(f"{path.name}:{node.lineno} ({recv}.write_text)")
    return offenders


class IndexWritesAreAtomicTests(unittest.TestCase):
    def test_no_script_writes_an_index_non_atomically(self) -> None:
        scripts = sorted(p for p in SCR.rglob("*.py")
                         if "tests" not in p.parts and p.name != "sdlc_md.py")
        self.assertGreater(len(scripts), 20, "script scan found nothing - the glob is wrong")
        offenders = [o for p in scripts for o in _non_atomic_index_writes(p)]
        self.assertEqual(
            offenders, [],
            "an _index.md write bypasses sdlc_md.atomic_write, reopening the torn-read "
            "window it exists to close - route it through atomic_write:\n  "
            + "\n  ".join(offenders))

    def test_guard_catches_a_planted_offender(self) -> None:
        # the guard is only worth having if it fails on a new offender: prove it does.
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "offender.py"
            p.write_text("from pathlib import Path\n"
                         "def f(root):\n"
                         "    p = root / 'bugs' / '_index.md'\n"
                         "    p.write_text('rows', encoding='utf-8')\n", encoding="utf-8")
            self.assertEqual(len(_non_atomic_index_writes(p)), 1)

    def test_guard_ignores_an_atomic_write(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "good.py"
            p.write_text("def f(root, sdlc_md):\n"
                         "    idx = root / 'bugs' / '_index.md'\n"
                         "    sdlc_md.atomic_write(idx, 'rows')\n", encoding="utf-8")
            self.assertEqual(_non_atomic_index_writes(p), [])

    def test_named_index_writers_still_index(self) -> None:
        # the writers this closed must keep their behaviour: content unchanged, only the
        # write mechanism. A meta_new row still lands in the index.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            r = artifact.meta_new(repo, "retro", "the sprint retro")
            self.assertTrue(r["indexed"])
            idx = (repo / "sdlc-studio" / "retros" / "_index.md").read_text(encoding="utf-8")
            self.assertIn(f"[{r['id']}]", idx)


class ConcurrentAllocationTests(unittest.TestCase):
    def test_concurrent_new_mints_distinct_ids(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
            ids: list[str] = []
            errors: list[Exception] = []
            lock = threading.Lock()

            def worker(i: int) -> None:
                try:
                    r = artifact.new(repo, "bug", f"defect number {i}",
                                     {"affects": "src/thing.py", "points": 3})
                    with lock:
                        ids.append(r["id"])
                except Exception as e:  # noqa: BLE001 - collect for the assertion
                    with lock:
                        errors.append(e)

            threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            self.assertEqual(errors, [], f"concurrent new raised: {errors}")
            self.assertEqual(len(set(ids)), 8, f"duplicate ids minted: {sorted(ids)}")

    def test_concurrent_file_finding_mints_distinct_ids(self) -> None:
        # BG0076: file_finding allocate+write was not under allocation_lock - concurrent
        # filers minted the same v2 id and clobbered index rows (RV0007 reproduced a 4-way).
        file_finding = _load("file_finding")
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _index(repo, "bug", "| ID | Title | Status | Severity | Created | Updated |")
            ids: list[str] = []
            errors: list[Exception] = []
            lock = threading.Lock()

            def worker(i: int) -> None:
                try:
                    r = file_finding.file_finding(
                        repo, "bug", f"finding {i}",
                        {"severity": "Medium", "summary": "s", "steps": "r", "fix": "f",
                         "affects": "src/thing.py", "points": 3})
                    with lock:
                        ids.append(r["id"])
                except Exception as e:  # noqa: BLE001
                    with lock:
                        errors.append(e)

            threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            self.assertEqual(errors, [], f"concurrent file_finding raised: {errors}")
            self.assertEqual(len(set(ids)), 8, f"duplicate ids minted: {sorted(ids)}")
            # every minted id also has exactly one index row (no clobber)
            idx = (repo / "sdlc-studio" / "bugs" / "_index.md").read_text(encoding="utf-8")
            for i in ids:
                self.assertEqual(idx.count(f"[{i}]"), 1, f"{i} row missing/duplicated")


if __name__ == "__main__":
    unittest.main()
