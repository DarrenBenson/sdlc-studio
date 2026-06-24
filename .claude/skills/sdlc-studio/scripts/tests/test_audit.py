"""Unit tests for audit.py - sprint tranche readiness (RED first)."""
from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "audit.py"


def _load():
    spec = importlib.util.spec_from_file_location("audit", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["audit"] = mod
    spec.loader.exec_module(mod)
    return mod


def _cr(root, num, status="Proposed", ac="- [ ] integrity.py exits 1 when an active story lacks its Epic link", depends=None):
    d = root / "sdlc-studio" / "change-requests"
    d.mkdir(parents=True, exist_ok=True)
    body = f"# CR-{num:04d}: c\n\n> **Status:** {status}\n"
    if depends:
        body += f"> **Depends on:** {depends}\n"
    body += f"\n## Acceptance Criteria\n\n{ac}\n"
    (d / f"CR{num:04d}-x.md").write_text(body, encoding="utf-8")


TAUTOLOGY = "- [ ] Change implemented and verified; lint and tests green."


def _bug(root, num, status="Open", repro=True, fix=True):
    d = root / "sdlc-studio" / "bugs"
    d.mkdir(parents=True, exist_ok=True)
    body = f"# BG{num:04d}: b\n\n> **Status:** {status}\n> **Severity:** Medium\n\n## Summary\n\nx\n"
    if repro:
        body += "\n## Steps to Reproduce\n\n1. do it\n"
    if fix:
        body += "\n## Proposed Fix\n\ndo this\n"
    (d / f"BG{num:04d}-x.md").write_text(body, encoding="utf-8")


class WeakAcTests(unittest.TestCase):
    def test_tautology_is_weak(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, ac=TAUTOLOGY)
            u = _load().audit_unit(root, "CR0001")
            self.assertFalse(u["ready"])
            self.assertIn("weak-AC", u["issues"])

    def test_concrete_ac_is_ready(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 2)  # concrete AC, Proposed, no deps
            u = _load().audit_unit(root, "CR0002")
            self.assertTrue(u["ready"], u["issues"])

    def test_empty_ac_is_weak(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 3, ac="(none yet)")
            u = _load().audit_unit(root, "CR0003")
            self.assertIn("weak-AC", u["issues"])

    def test_prose_only_ac_with_markup_elsewhere_is_weak(self) -> None:
        # AC-style markup OUTSIDE the AC section must not count; a prose-only AC
        # section is weak even if `- **AC1:**` appears in the Summary.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cdir = root / "sdlc-studio" / "change-requests"
            cdir.mkdir(parents=True, exist_ok=True)
            (cdir / "CR0009-x.md").write_text(
                "# CR-0009: c\n\n> **Status:** Proposed\n\n"
                "## Summary\n\n- **AC1:** this looks like an AC but is in Summary\n\n"
                "## Acceptance Criteria\n\nThe change should work well.\n",
                encoding="utf-8")
            u = _load().audit_unit(root, "CR0009")
            self.assertIn("weak-AC", u["issues"])


class DepsTerminalTests(unittest.TestCase):
    def test_unmet_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, status="Proposed")          # dependency, not yet done
            _cr(root, 2, status="Proposed", depends="CR0001")
            u = _load().audit_unit(root, "CR0002")
            self.assertFalse(u["ready"])
            self.assertTrue(any("CR0001" in i for i in u["issues"]))

    def test_met_dependency_ok(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, status="Complete")
            _cr(root, 2, status="Proposed", depends="CR0001")
            u = _load().audit_unit(root, "CR0002")
            self.assertTrue(u["ready"], u["issues"])

    def test_already_terminal(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 4, status="Complete")
            u = _load().audit_unit(root, "CR0004")
            self.assertFalse(u["ready"])
            self.assertIn("already-terminal", u["issues"])

    def test_missing_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 2, status="Proposed", depends="CR9099")  # referent absent
            u = _load().audit_unit(root, "CR0002")
            self.assertFalse(u["ready"])
            self.assertTrue(any("CR9099:missing" in i for i in u["issues"]))

    def test_dead_dependency_surfaced(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, status="Rejected")
            _cr(root, 2, status="Proposed", depends="CR0001")
            u = _load().audit_unit(root, "CR0002")
            self.assertFalse(u["ready"])
            self.assertTrue(any("dead" in i for i in u["issues"]))


class LinkIntegrityTests(unittest.TestCase):
    def test_link_integrity_plumbing(self) -> None:
        # An active story with a `--` Epic is an integrity error; audit_batch must
        # surface it as a link-integrity issue (proves the integrity_errors wiring).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True, exist_ok=True)
            (sd / "US0001-x.md").write_text(
                "# US0001: s\n\n> **Status:** Ready\n> **Epic:** --\n\n"
                "## Acceptance Criteria\n\n### AC1: real thing\n", encoding="utf-8")
            res = _load().audit_batch(root, ["US0001"])
            self.assertIn("link-integrity", res["units"][0]["issues"])


class BugReadinessTests(unittest.TestCase):
    def test_well_formed_bug_is_ready_not_weak_ac(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1, repro=True, fix=True)   # has Steps + Proposed Fix
            u = _load().audit_unit(root, "BG0001")
            self.assertTrue(u["ready"], u["issues"])
            self.assertNotIn("weak-AC", u["issues"])

    def test_underspecified_bug_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 2, repro=False, fix=False)
            u = _load().audit_unit(root, "BG0002")
            self.assertFalse(u["ready"])
            self.assertIn("underspecified", u["issues"])
            self.assertNotIn("weak-AC", u["issues"])

    def test_bug_with_suffixed_headings_ready(self) -> None:
        # Heading match is substring-tolerant: "## Steps to Reproduce the crash" counts.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            dd = root / "sdlc-studio" / "bugs"
            dd.mkdir(parents=True, exist_ok=True)
            (dd / "BG0003-x.md").write_text(
                "# BG0003: b\n\n> **Status:** Open\n\n## Steps to Reproduce the crash\n\n"
                "1. x\n\n## Proposed Fix and rationale\n\ny\n", encoding="utf-8")
            u = _load().audit_unit(root, "BG0003")
            self.assertTrue(u["ready"], u["issues"])


class GuidanceTests(unittest.TestCase):
    def test_guidance_printed(self) -> None:
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, ac=TAUTOLOGY)  # weak-AC -> not ready
            buf = io.StringIO()
            with redirect_stdout(buf):
                _load().main(["check", "--ids", "CR0001", "--root", str(root)])
            out = buf.getvalue()
            self.assertIn("Guidance:", out)
            self.assertIn("weak-AC ->", out)


class CliTests(unittest.TestCase):
    def test_batch_json_and_exit(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, ac=TAUTOLOGY)   # not ready
            _cr(root, 2)                  # ready
            mod = _load()
            res = mod.audit_batch(root, ["CR0001", "CR0002"])
            self.assertEqual(res["summary"]["total"], 2)
            self.assertEqual(res["summary"]["not_ready"], 1)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = mod.main(["check", "--ids", "CR0001,CR0002", "--root", str(root), "--format", "json"])
            self.assertEqual(rc, 1)  # a not-ready unit -> non-zero
            self.assertIn("summary", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
