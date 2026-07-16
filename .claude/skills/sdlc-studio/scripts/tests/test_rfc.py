"""Unit tests for rfc.py - RFC decision-readiness digest (CR0024). RED first."""
from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib import sdlc_md  # noqa: E402

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
    def test_all_resolved_rows_read_decided_not_ready(self) -> None:
        # BG0177: decided-awaiting-delivery must never read READY-for-decision -
        # the digest was inviting the operator to re-decide settled questions
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rfc(root, 1, n_decisions=2, n_open=0, n_workstreams=3)  # all resolved
            r = _by_id(root)["RFC0001"]
            self.assertEqual(r["open_count"], 0)
            self.assertEqual(r["workstreams"], 3)
            self.assertTrue(r["decided"])
            self.assertFalse(r["ready_for_decision"])

    def test_ready_when_recommendation_and_no_decision_rows(self) -> None:
        # nothing decided yet + a recommendation = genuinely ready for the session
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rfc(root, 1)  # no decisions table at all
            r = _by_id(root)["RFC0001"]
            self.assertFalse(r["decided"])
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


class DecideChildrenTests(unittest.TestCase):
    """BG0177: ws counts the RFC's real children (the Decomposed-into/Parent links every
    other tool uses), falling back to the Workstream table only when no children exist."""

    def _child_cr(self, root, num, parent):
        d = root / "sdlc-studio" / "change-requests"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"CR{num:04d}-x.md").write_text(
            f"# CR-{num:04d}: c\n\n> **Status:** Proposed\n> **Parent:** {parent}\n",
            encoding="utf-8")

    def test_ws_counts_linked_children(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rfc(root, 1, n_decisions=1, n_open=1)
            self._child_cr(root, 10, "RFC0001")
            self._child_cr(root, 11, "RFC0001")
            r = _by_id(root)["RFC0001"]
            self.assertEqual(r["workstreams"], 2)

    def test_ws_falls_back_to_table_without_children(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rfc(root, 1, n_workstreams=3)
            self.assertEqual(_by_id(root)["RFC0001"]["workstreams"], 3)

    def test_decided_line_printed_as_decided(self) -> None:
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rfc(root, 1, n_decisions=2, n_open=0)
            self._child_cr(root, 10, "RFC0001")
            mod = _load()
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                mod.main(["decide", "--root", str(root)])
            out = buf.getvalue()
            self.assertIn("DECIDED", out)
            self.assertNotIn("READY RFC0001", out)
            self.assertIn("ws=1", out)


class ParentMintTests(unittest.TestCase):
    """US0191: --parent wires BOTH link directions atomically at mint - the 9
    hand-caused asymmetries of the 2026-07-17 triage become impossible."""

    def _fixture_rfc(self, root):
        _rfc(root, 1, n_decisions=1, n_open=1)

    def test_parent_mint_wires_both_directions(self) -> None:
        import importlib.util as ilu
        spec = ilu.spec_from_file_location(
            "file_finding", Path(__file__).resolve().parent.parent / "file_finding.py")
        ff = ilu.module_from_spec(spec)
        sys.modules["file_finding"] = ff
        spec.loader.exec_module(ff)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture_rfc(root)
            (root / "src").mkdir()
            (root / "src" / "x.py").write_text("", encoding="utf-8")
            res = ff.file_finding(root, "cr", "child of the rfc",
                                  {"priority": "Medium", "ctype": "Improvement",
                                   "summary": "s", "impact": "i", "size": "S",
                                   "affects": "src/x.py",
                                   "acs": ["a criterion"], "parent": "RFC0001"})
            child = Path(res["path"]).read_text(encoding="utf-8")
            self.assertIn("> **Parent:** RFC0001", child)
            rfc_text = sdlc_md.find_by_id(root, "RFC0001")[0].read_text(encoding="utf-8")
            self.assertIn(res["id"].replace("-", ""), rfc_text.replace("-", ""))
            self.assertEqual(sdlc_md.children_of(root, "RFC0001"),
                             [(sdlc_md.norm_id(res["id"]), "cr")])

    def test_parent_mint_unknown_parent_refused_nothing_minted(self) -> None:
        import importlib.util as ilu
        spec = ilu.spec_from_file_location(
            "file_finding", Path(__file__).resolve().parent.parent / "file_finding.py")
        ff = ilu.module_from_spec(spec)
        sys.modules["file_finding"] = ff
        spec.loader.exec_module(ff)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with self.assertRaises(ValueError):
                ff.file_finding(root, "cr", "orphan",
                                {"priority": "Medium", "ctype": "Improvement",
                                 "summary": "s", "impact": "i", "size": "S",
                                 "affects": "src/x.py",
                                 "acs": ["a"], "parent": "RFC0999"})
            crs = root / "sdlc-studio" / "change-requests"
            self.assertFalse(crs.is_dir() and list(crs.glob("CR*.md")))


class ParentMintCliTests(unittest.TestCase):
    """The CLI path is the ceremony's documented entrypoint - the critic proved the
    flag was silently dropped there while the API tests stayed green."""

    def _ff_main(self, root, *extra):
        import contextlib
        import io
        import importlib.util as ilu
        spec = ilu.spec_from_file_location(
            "file_finding", Path(__file__).resolve().parent.parent / "file_finding.py")
        ff = ilu.module_from_spec(spec)
        sys.modules["file_finding"] = ff
        spec.loader.exec_module(ff)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = ff.main(["file", "--type", "cr", "--title", "cli child",
                          "--priority", "Medium", "--ctype", "Improvement",
                          "--summary", "s", "--impact", "i", "--size", "S",
                          "--affects", "src/x.py", "--ac", "a criterion",
                          "--root", str(root), *extra])
        return rc, out.getvalue(), err.getvalue()

    def test_cli_parent_wires_both_directions(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rfc(root, 1, n_decisions=1, n_open=1)
            (root / "src").mkdir()
            (root / "src" / "x.py").write_text("", encoding="utf-8")
            rc, _, err = self._ff_main(root, "--parent", "RFC0001")
            self.assertEqual(rc, 0, err)
            children = sdlc_md.children_of(root, "RFC0001")
            self.assertEqual(len(children), 1)

    def test_cli_unknown_parent_refused_nonzero(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "src").mkdir()
            (root / "src" / "x.py").write_text("", encoding="utf-8")
            rc, _, err = self._ff_main(root, "--parent", "RFC0999")
            self.assertNotEqual(rc, 0)
            self.assertIn("RFC0999", err)


class ResolveTests(unittest.TestCase):
    """US0191: rfc resolve edits exactly the named decision row - the judgement is
    the operator's, the table surgery stops being regex heredocs."""

    def _resolve(self, root, *args):
        import contextlib
        import io
        mod = _load()
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = mod.main(["resolve", "--root", str(root), *args])
        return rc, out.getvalue(), err.getvalue()

    def test_resolve_edits_exactly_the_named_row(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rfc(root, 1, n_decisions=3, n_open=3)
            before = sdlc_md.find_by_id(root, "RFC0001")[0].read_text(encoding="utf-8")
            rc, _, _ = self._resolve(root, "--rfc", "RFC0001", "--decision", "D2",
                                     "--resolution", "option B wins", "--refs", "CR0100")
            self.assertEqual(rc, 0)
            after = sdlc_md.find_by_id(root, "RFC0001")[0].read_text(encoding="utf-8")
            self.assertIn("| D2 | something | Resolved: option B wins -> CR0100 |", after)
            for line in before.splitlines():
                if "| D1 |" in line or "| D3 |" in line:
                    self.assertIn(line, after)   # untouched rows byte-identical
            self.assertIn("resolve: D2", after)  # revision row appended

    def test_resolve_unknown_rfc_and_decision_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rfc(root, 1, n_decisions=1, n_open=1)
            rc, _, err = self._resolve(root, "--rfc", "RFC0009", "--decision", "D1",
                                       "--resolution", "x")
            self.assertNotEqual(rc, 0)
            rc, _, err = self._resolve(root, "--rfc", "RFC0001", "--decision", "D9",
                                       "--resolution", "x")
            self.assertNotEqual(rc, 0)
            self.assertIn("D9", err)


    def test_resolve_never_edits_a_body_table_with_a_matching_first_cell(self) -> None:
        # the critic's live probe: an Options Considered table containing | D2 | ...
        # must never be touched - the search is scoped to the Open Decisions section
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rfc_dir = root / "sdlc-studio" / "rfcs"
            rfc_dir.mkdir(parents=True)
            (rfc_dir / "RFC0001-x.md").write_text(
                "# RFC-0001: title\n\n> **Status:** Draft\n\n"
                "## Options Considered\n\n| # | Option | Verdict |\n| --- | --- | --- |\n"
                "| D2 | reuse the digest | rejected |\n\n"
                "## Recommendation\n\nUse Option B.\n\n"
                "## Open Decisions\n\n| # | Decision | Status |\n| --- | --- | --- |\n"
                "| D2 | the real decision | Open |\n", encoding="utf-8")
            rc, _, _ = self._resolve(root, "--rfc", "RFC0001", "--decision", "D2",
                                     "--resolution", "settled")
            self.assertEqual(rc, 0)
            after = (rfc_dir / "RFC0001-x.md").read_text(encoding="utf-8")
            self.assertIn("| D2 | reuse the digest | rejected |", after)   # body table untouched
            self.assertIn("| D2 | the real decision | Resolved: settled |", after)

    def test_revision_row_lands_inside_the_table_not_at_eof(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rfc_dir = root / "sdlc-studio" / "rfcs"
            rfc_dir.mkdir(parents=True)
            (rfc_dir / "RFC0001-x.md").write_text(
                "# RFC-0001: title\n\n> **Status:** Draft\n\n"
                "## Recommendation\n\nB.\n\n"
                "## Open Decisions\n\n| # | Decision | Status |\n| --- | --- | --- |\n"
                "| D1 | x | Open |\n\n"
                "## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
                "| 2026-07-01 | t | Filed |\n\n"
                "## Appendix\n\ntrailing section\n", encoding="utf-8")
            rc, _, _ = self._resolve(root, "--rfc", "RFC0001", "--decision", "D1",
                                     "--resolution", "done")
            self.assertEqual(rc, 0)
            after = (rfc_dir / "RFC0001-x.md").read_text(encoding="utf-8")
            hist = after.split("## Revision History", 1)[1].split("## Appendix", 1)[0]
            self.assertIn("resolve: D1", hist)     # inside the table section
            self.assertFalse(after.rstrip().endswith("|") and "resolve: D1" in after.splitlines()[-1])


if __name__ == "__main__":
    unittest.main()
