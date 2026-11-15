"""`escape.py to-class` turns a confirmed escape's root cause into a failure class.

The class is written through `lessons.class_add`, the function `lessons.py class-add` runs, so the
row carries the next `LC-` code, the open run and the source like every other recorded class. It
is injected at build and review, its `evidence` cites the bug and the unit that let it through,
and its `files` holds the bug's Affects paths, so a later unit touching those files can be matched
to it. A bug that is not a confirmed escape, a Root Cause still holding the scaffold, and a class
the store already holds are each refused with exit 2, the store byte-identical.

Driven through `escape.main`, the shipped entry point, in throwaway project roots.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

escape = loader.load_script("escape")
file_finding = loader.load_script("file_finding")

STORE = Path("sdlc-studio") / "lessons.jsonl"
KNOWN = {"id": "LC-001", "class": "mutant never applied",
         "rule": "Assert a mutation applied before trusting its verdict.",
         "behaviour": "Count the replaced text first.", "inject": ["build"], "hits": [],
         "state": "active", "recorded_run": "RUN-OLD", "recorded_source": "retro:RETRO0001"}
CAUSE = ("The review approved a total that was never tested at the empty basket, so the "
         "boundary shipped unpinned.")


def _cli(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = escape.main(argv)
    return rc, out.getvalue(), err.getvalue()


def _bug(root: Path, bid: str = "BG0001", *, escaped: bool = True, via: str | None = "US0002",
         cause: str | None = CAUSE, affects: str = "scripts/a.py, scripts/b.py") -> None:
    head = f"# {bid}: the total is wrong\n\n> **Status:** Open\n> **Affects:** {affects}\n"
    if escaped:
        head += "> **Escaped:** yes\n> **Shipped-in:** v1.0.0\n"
        if via:
            head += f"> **Escaped-via:** {via}\n"
    body = "\n## Summary\n\nthe total is wrong\n"
    if cause is not None:
        body += f"\n## Root Cause\n\n{cause}\n"
    (root / "sdlc-studio" / "bugs" / f"{bid}-the-total-is-wrong.md").write_text(
        head + body, encoding="utf-8")


def _project(d: str) -> Path:
    root = Path(d)
    (root / "sdlc-studio" / "bugs").mkdir(parents=True)
    (root / STORE).write_text(json.dumps(KNOWN) + "\n", encoding="utf-8")
    return root


def _args(bug: str = "BG0001", name: str = "a boundary never pinned") -> list[str]:
    return ["to-class", "--bug", bug, "--class", name,
            "--rule", "A boundary the criteria name is pinned by a test before review.",
            "--behaviour", "Name the boundary in the criterion and pin it.", "--format", "json"]


def _snapshot(root: Path) -> dict[str, bytes]:
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*"))
            if p.is_file()}


class EscapeClassTests(unittest.TestCase):

    def test_a_root_cause_becomes_a_class_row_carrying_its_files(self):
        with tempfile.TemporaryDirectory() as d:
            root = _project(d)
            _bug(root)
            before = _snapshot(root)
            with mock.patch.object(escape.lessons, "class_add",
                                   wraps=escape.lessons.class_add) as spy:
                rc, out, err = _cli(_args() + ["--root", str(root)])
            self.assertEqual(rc, 0, err)
            spy.assert_called_once()
            rows = [json.loads(ln) for ln in (root / STORE).read_text(encoding="utf-8")
                    .splitlines() if ln.strip()]
            self.assertEqual(len(rows), 2, rows)
            self.assertEqual(rows[0], KNOWN)
            row = rows[1]
            self.assertEqual(row["id"], "LC-002")
            self.assertEqual(row["class"], "a boundary never pinned")
            self.assertEqual(row["inject"], ["build", "review"])
            self.assertEqual(row["state"], "active")
            self.assertEqual(row["hits"], [])
            self.assertEqual(row["evidence"], ["BG0001", "US0002"])
            self.assertEqual(row["files"], ["scripts/a.py", "scripts/b.py"])
            self.assertEqual(row["recorded_source"], "escape:BG0001")
            self.assertEqual(json.loads(out)["id"], "LC-002")
            # The store is the one file the verb changed.
            after = _snapshot(root)
            changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
            self.assertEqual(changed, [str(STORE)])

    def test_text_output_names_the_class_and_its_files(self):
        with tempfile.TemporaryDirectory() as d:
            root = _project(d)
            _bug(root)
            argv = [a for a in _args() if a not in ("--format", "json")]
            rc, out, err = _cli(argv + ["--root", str(root)])
            self.assertEqual(rc, 0, err)
            self.assertIn("LC-002", out)
            self.assertIn("scripts/a.py", out)

    def test_an_unescaped_empty_or_duplicate_class_is_refused(self):
        cases = {
            "not escaped": (dict(escaped=False), "a boundary never pinned", "not escaped"),
            "unconfirmed": (dict(via=None), "a boundary never pinned", "Escaped-via"),
            "scaffold": (dict(cause=file_finding.ROOT_CAUSE_SCAFFOLD),
                         "a boundary never pinned", "Root Cause"),
            "no section": (dict(cause=None), "a boundary never pinned", "Root Cause"),
            "duplicate": ({}, "Mutant Never-Applied", "LC-001"),
        }
        for label, (bug_kw, name, reason) in cases.items():
            with self.subTest(label), tempfile.TemporaryDirectory() as d:
                root = _project(d)
                _bug(root, **bug_kw)
                before = _snapshot(root)
                rc, out, err = _cli(_args(name=name) + ["--root", str(root)])
                self.assertEqual(rc, 2, f"{label}: {out}{err}")
                self.assertIn("to-class refused", err)
                self.assertIn(reason, err)
                self.assertEqual(_snapshot(root), before, f"{label} changed the project")

    def test_a_bug_that_does_not_exist_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = _project(d)
            rc, _, err = _cli(_args(bug="BG0099") + ["--root", str(root)])
            self.assertEqual(rc, 2)
            self.assertIn("BG0099", err)


if __name__ == "__main__":
    unittest.main()
