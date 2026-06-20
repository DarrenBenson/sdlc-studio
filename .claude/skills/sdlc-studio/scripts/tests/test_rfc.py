"""Unit tests for rfc.py - RFC decision-readiness digest (CR0024). RED first."""
from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "rfc.py"


def _load():
    spec = importlib.util.spec_from_file_location("rfc", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["rfc"] = mod
    spec.loader.exec_module(mod)
    return mod


def _rfc(root, num, status="Draft", n_decisions=0, n_open=0, n_workstreams=0, recommendation="Use Option B."):
    d = root / "sdlc-studio" / "rfcs"
    d.mkdir(parents=True, exist_ok=True)
    p = [f"# RFC-{num:04d}: title", "", f"> **Status:** {status}", "",
         "## Recommendation", "", recommendation, ""]
    if n_decisions:
        p += ["## Open Decisions", "", "| # | Decision | Status |", "| --- | --- | --- |"]
        for i in range(n_decisions):
            p.append(f"| D{i+1} | something | {'Open' if i < n_open else 'Resolved'} |")
        p.append("")
    if n_workstreams:
        p += ["## Phased Plan / Workstreams", "", "| WS | Workstream | Becomes |", "| --- | --- | --- |"]
        for i in range(n_workstreams):
            p.append(f"| WS{i+1} | do x | CR (TBD) |")
        p.append("")
    (d / f"RFC{num:04d}-x.md").write_text("\n".join(p) + "\n", encoding="utf-8")


def _by_id(root):
    return {r["id"]: r for r in _load().digest(root)["rfcs"]}


class DigestTests(unittest.TestCase):
    def test_ready_when_recommendation_and_no_open(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rfc(root, 1, n_decisions=2, n_open=0, n_workstreams=3)  # all resolved
            r = _by_id(root)["RFC0001"]
            self.assertEqual(r["open_count"], 0)
            self.assertEqual(r["open_decisions"], 2)
            self.assertEqual(r["workstreams"], 3)
            self.assertTrue(r["has_recommendation"])
            self.assertTrue(r["ready_for_decision"])

    def test_not_ready_with_open_decisions(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rfc(root, 1, n_decisions=3, n_open=2)
            r = _by_id(root)["RFC0001"]
            self.assertEqual(r["open_count"], 2)
            self.assertFalse(r["ready_for_decision"])

    def test_not_ready_without_recommendation(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rfc(root, 1, recommendation="TBD")
            r = _by_id(root)["RFC0001"]
            self.assertFalse(r["has_recommendation"])
            self.assertFalse(r["ready_for_decision"])

    def test_first_table_only_and_subheading_kept(self) -> None:
        # A ### subheading must not end the section, and only the first table counts.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rd = root / "sdlc-studio" / "rfcs"
            rd.mkdir(parents=True)
            (rd / "RFC0001-x.md").write_text(
                "# RFC-0001: t\n\n> **Status:** Draft\n\n## Recommendation\n\nUse B.\n\n"
                "## Open Decisions\n\n| # | Decision | Status |\n| --- | --- | --- |\n"
                "| D1 | a | Resolved |\n\n### A subheading\n\n| X | Y |\n| --- | --- |\n| p | q |\n\n"
                "## Next\n\ntext\n", encoding="utf-8")
            r = _by_id(root)["RFC0001"]
            self.assertEqual(r["open_decisions"], 1)
            self.assertEqual(r["open_count"], 0)

    def test_only_exact_open_status_counts(self) -> None:
        # "Resolved"/"Deferred" and a "Reopen" in the Decision cell must not count.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rd = root / "sdlc-studio" / "rfcs"
            rd.mkdir(parents=True)
            (rd / "RFC0001-x.md").write_text(
                "# RFC-0001: t\n\n> **Status:** Draft\n\n## Recommendation\n\nUse B.\n\n"
                "## Open Decisions\n\n| # | Decision | Status |\n| --- | --- | --- |\n"
                "| D1 | a | Open |\n| D2 | b | Resolved |\n| D3 | Reopen later | Deferred |\n\n## Next\n\nx\n",
                encoding="utf-8")
            r = _by_id(root)["RFC0001"]
            self.assertEqual(r["open_decisions"], 3)
            self.assertEqual(r["open_count"], 1)

    def test_accepted_excluded_from_draft_digest(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rfc(root, 1, status="Accepted")
            self.assertNotIn("RFC0001", _by_id(root))  # only Draft/In Review by default


class CliTests(unittest.TestCase):
    def test_decide_json(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rfc(root, 1)
            mod = _load()
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = mod.main(["decide", "--root", str(root), "--format", "json"])
            self.assertEqual(rc, 0)
            self.assertIn("rfcs", buf.getvalue())


class EscapedPipeTests(unittest.TestCase):
    """RFC tables are human-authored; an escaped pipe must not shift columns (BG0021)."""

    def test_workstream_cell_with_escaped_pipe(self) -> None:
        rfc = _load()
        lines = [
            "| WS | Workstream | Becomes |",
            "| --- | --- | --- |",
            r"| WS1 | match `All\|Crew` fields | CR (TBD) |",
        ]
        rows = rfc._table_data_rows(lines)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0], ["WS1", "match `All|Crew` fields", "CR (TBD)"])


if __name__ == "__main__":
    unittest.main()
