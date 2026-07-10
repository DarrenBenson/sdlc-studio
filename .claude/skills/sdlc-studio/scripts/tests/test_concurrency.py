"""US0069/CR0183: passive concurrency safety - atomic index writes and an advisory
allocation lock, so the ledger stays safe under concurrent writers.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
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
                    r = artifact.new(repo, "bug", f"defect number {i}")
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
                        {"severity": "Medium", "summary": "s", "steps": "r", "fix": "f"})
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
