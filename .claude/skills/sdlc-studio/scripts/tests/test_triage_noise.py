"""Unit tests for the v3 triage noise controls (US0067): Low-severity consolidation and the
per-session creation cap. Enforced at creation time and dormant under schema_version 2.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, DIR / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


tn = _load("triage_noise", "triage_noise.py")
ff = _load("file_finding", "file_finding.py")


def _repo(root: Path, cap: int = 20, v3: bool = True, low_consolidation: bool = True) -> Path:
    """A repo with bug + change-request indexes; opt into v3 + a triage config when asked."""
    sd = root / "sdlc-studio"
    sd.mkdir(parents=True, exist_ok=True)
    if v3:
        (sd / ".config.yaml").write_text(
            f"schema_version: 3\ntriage:\n  session_cap: {cap}\n"
            f"  low_consolidation: {'true' if low_consolidation else 'false'}\n",
            encoding="utf-8")
    for rel, header, summary in (
        ("bugs", "| ID | Title | Status | Severity | Created | Updated |",
         "| inbox | 0 |\n| Open | 0 |\n| Fixed | 0 |"),
        ("change-requests",
         "| ID | Title | Status | Priority | Type | Date | Linked Epics |",
         "| inbox | 0 |\n| Proposed | 0 |\n| Complete | 0 |")):
        d = sd / rel
        d.mkdir(parents=True, exist_ok=True)
        sep = "|" + " --- |" * (header.count("|") - 1)
        (d / "_index.md").write_text(
            f"# Index\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n{summary}\n"
            f"| **Total** | **0** |\n\n## All\n\n{header}\n{sep}\n", encoding="utf-8")
    return root


def _bug(severity: str) -> dict:
    return {"severity": severity, "summary": "s", "steps": "r", "fix": "f"}


class ConsolidationTests(unittest.TestCase):
    """AC1: a Low-severity finding folds into a themed consolidation CR; Medium+ stays individual."""

    def test_consolidate_low_finding_into_cr(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            res = ff.file_finding(root, "bug", "a nit", _bug("low"))
            self.assertTrue(res.get("consolidated_into"))            # folded, not standalone
            self.assertFalse(list((root / "sdlc-studio" / "bugs").glob("BG*.md")))  # no bug file
            cr = Path(res["path"]).read_text(encoding="utf-8")
            self.assertIn("## Consolidated Findings", cr)
            self.assertIn("a nit", cr)
            self.assertIn("> **Consolidation:** low-severity-bugs", cr)  # separator-safe slug marker

    def test_consolidate_theme_with_field_separator_stays_one_cr(self) -> None:
        # A theme containing `·` (the inline metadata separator) must still match on read-back -
        # the marker is a slug, so extract_field cannot truncate it into a fresh CR per finding.
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            a = ff.file_finding(root, "bug", "one", {**_bug("low"), "theme": "auth · session"})
            b = ff.file_finding(root, "bug", "two", {**_bug("low"), "theme": "auth · session"})
            self.assertEqual(a["consolidated_into"], b["consolidated_into"])
            self.assertEqual(len(list((root / "sdlc-studio" / "change-requests").glob("CR*.md"))), 1)

    def test_consolidate_theme_case_and_whitespace_insensitive(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            a = ff.file_finding(root, "bug", "one", {**_bug("low"), "theme": "Perf Path"})
            b = ff.file_finding(root, "bug", "two", {**_bug("low"), "theme": "perf   path"})
            self.assertEqual(a["consolidated_into"], b["consolidated_into"])

    def test_consolidate_second_low_appends_to_same_cr(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            first = ff.file_finding(root, "bug", "nit one", _bug("low"))
            second = ff.file_finding(root, "bug", "nit two", _bug("low"))
            self.assertEqual(first["consolidated_into"], second["consolidated_into"])  # one CR
            crs = list((root / "sdlc-studio" / "change-requests").glob("CR*.md"))
            self.assertEqual(len(crs), 1)
            body = crs[0].read_text(encoding="utf-8")
            self.assertIn("nit one", body)
            self.assertIn("nit two", body)

    def test_consolidate_low_with_tranche_flags_the_drop(self) -> None:
        # A record-only tranche cannot ride onto a shared consolidation CR; the drop must be
        # visible (fail loud, not silent) - the EP0014 principle applied to a cross-unit edge.
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            res = ff.file_finding(root, "bug", "a nit", {**_bug("low"), "tranche": "sprint-14"})
            self.assertTrue(res.get("consolidated_into"))
            self.assertEqual(res.get("tranche_dropped"), "sprint-14")
            cr = Path(res["path"]).read_text(encoding="utf-8")
            self.assertNotIn("Tranche", cr)   # not silently written onto the shared CR

    def test_consolidate_medium_stays_individual(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            res = ff.file_finding(root, "bug", "a real defect", _bug("medium"))
            self.assertIsNone(res.get("consolidated_into"))
            self.assertIn("> **Status:** inbox", Path(res["path"]).read_text(encoding="utf-8"))

    def test_consolidate_dormant_under_v2(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), v3=False)
            res = ff.file_finding(root, "bug", "a nit", _bug("low"))
            self.assertIsNone(res.get("consolidated_into"))          # filed individually on v2
            self.assertIn("> **Status:** Open", Path(res["path"]).read_text(encoding="utf-8"))

    def test_consolidate_off_when_low_consolidation_false(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), low_consolidation=False)
            res = ff.file_finding(root, "bug", "a nit", _bug("low"))
            self.assertIsNone(res.get("consolidated_into"))          # individual, into inbox


class SessionCapTests(unittest.TestCase):
    """AC2: the N+1th finding in a session is refused loudly."""

    def test_session_cap_refuses_the_n_plus_first(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cap=2)
            ff.file_finding(root, "bug", "one", _bug("medium"))      # 1
            ff.file_finding(root, "bug", "two", _bug("medium"))      # 2
            with self.assertRaises(ValueError) as ctx:
                ff.file_finding(root, "bug", "three", _bug("medium"))  # 3 -> refused
            self.assertIn("session cap reached", str(ctx.exception).lower())

    def test_session_cap_dormant_under_v2(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cap=2, v3=False)
            for t in ("one", "two", "three"):                        # cap not enforced on v2
                ff.file_finding(root, "bug", t, _bug("medium"))
            self.assertEqual(len(list((root / "sdlc-studio" / "bugs").glob("BG*.md"))), 3)

    def test_consolidated_appends_do_not_consume_budget(self) -> None:
        # Opening a consolidation CR mints one artefact (counts once); appending Low findings to
        # it mints nothing, so a Low flood cannot exhaust the session cap.
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cap=2)
            for t in ("nit a", "nit b", "nit c", "nit d"):
                ff.file_finding(root, "bug", t, _bug("low"))
            self.assertEqual(tn.session_count(root), 1)              # only the CR open counted


if __name__ == "__main__":
    unittest.main()
