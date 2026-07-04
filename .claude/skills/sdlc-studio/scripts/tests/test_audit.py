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

    def test_template_vocabulary_bug_ready(self) -> None:
        # The shipped template's heading names are the second accepted vocabulary.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            dd = root / "sdlc-studio" / "bugs"
            dd.mkdir(parents=True, exist_ok=True)
            (dd / "BG0004-x.md").write_text(
                "# BG0004: b\n\n> **Status:** Open\n\n## Reproduction Steps\n\n"
                "1. x\n\n## Fix Description\n\ny\n", encoding="utf-8")
            u = _load().audit_unit(root, "BG0004")
            self.assertTrue(u["ready"], u["issues"])

    def test_mixed_vocabulary_bug_ready(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            dd = root / "sdlc-studio" / "bugs"
            dd.mkdir(parents=True, exist_ok=True)
            (dd / "BG0005-x.md").write_text(
                "# BG0005: b\n\n> **Status:** Open\n\n## Reproduction Steps\n\n"
                "1. x\n\n## Proposed Fix\n\ny\n", encoding="utf-8")
            u = _load().audit_unit(root, "BG0005")
            self.assertTrue(u["ready"], u["issues"])

    def test_shipped_template_renders_ready(self) -> None:
        # The gate validated against its own template's output: a bug authored from
        # templates/core/bug.md with every placeholder filled must not flag underspecified.
        template = Path(__file__).resolve().parents[2] / "templates" / "core" / "bug.md"
        rendered = template.read_text(encoding="utf-8")
        import re
        rendered = re.sub(r"\{\{[^}]*\}\}", "filled", rendered)
        self.assertFalse(_load()._bug_underspecified(rendered),
                         "shipped bug template flags underspecified when fully filled")

    def test_bug_missing_both_sections_still_flags(self) -> None:
        # True positive preserved: neither vocabulary present -> underspecified.
        self.assertTrue(_load()._bug_underspecified(
            "# BG0006: b\n\n> **Status:** Open\n\n## Summary\n\nx\n"))

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


class SequencedInBatchTests(unittest.TestCase):
    """A dependency satisfied by the SAME tranche is the planner doing its job -
    informational `sequenced-in-batch`, not `unmet-deps`."""

    def test_in_batch_dep_is_informational_not_unmet(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1)
            _cr(root, 2, depends="CR0001")
            res = _load().audit_batch(root, ["CR0001", "CR0002"])
            u2 = next(u for u in res["units"] if u["id"] == "CR0002")
            self.assertTrue(u2["ready"], u2["issues"])
            self.assertNotIn("unmet-deps", "; ".join(u2["issues"]))
            self.assertIn("sequenced-in-batch: CR0001", "; ".join(u2.get("info", [])))

    def test_dead_in_batch_dep_stays_unmet(self) -> None:
        # A Rejected dep cannot be delivered by sequencing - keep it unmet-deps.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, status="Rejected")
            _cr(root, 2, depends="CR0001")
            res = _load().audit_batch(root, ["CR0001", "CR0002"])
            u2 = next(u for u in res["units"] if u["id"] == "CR0002")
            self.assertFalse(u2["ready"])
            self.assertIn("unmet-deps", "; ".join(u2["issues"]))

    def test_out_of_batch_dep_still_unmet(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1)
            _cr(root, 2, depends="CR0009")   # not in batch, not on disk
            res = _load().audit_batch(root, ["CR0001", "CR0002"])
            u2 = next(u for u in res["units"] if u["id"] == "CR0002")
            self.assertFalse(u2["ready"])
            self.assertIn("unmet-deps", "; ".join(u2["issues"]))


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


class AlreadySatisfiedTests(unittest.TestCase):
    """CR0098: a Ready unit whose verifiers all pass is flagged already-satisfied."""

    def _story(self, root, num=1, status="Ready"):
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"US{num:04d}-x.md").write_text(
            f"# US{num:04d}: s\n\n> **Status:** {status}\n\n## Acceptance Criteria\n\n"
            "### AC1\n- **Verify:** shell true\n", encoding="utf-8")

    def _report(self, root, stem, payload):
        import json
        rp = root / "sdlc-studio" / ".local" / "verify-report.json"
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps({"stories": {stem: payload}}), encoding="utf-8")

    def test_all_green_ready_unit_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, 1)
            self._report(root, "US0001-x", {"ac_count": 1, "verified": 1, "failed": 0, "stale": 0})
            r = _load().audit_unit(root, "US0001")
            self.assertIn("already-satisfied", r["issues"])

    def test_failing_unit_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, 2)
            self._report(root, "US0002-x", {"ac_count": 2, "verified": 1, "failed": 1, "stale": 0})
            r = _load().audit_unit(root, "US0002")
            self.assertNotIn("already-satisfied", r["issues"])


class CR0109AuditChecks(unittest.TestCase):
    """The tranche audit flags non-executable Verify lines + cross-epic AC leakage."""

    def _story(self, root, num, verify=None, ac_text="given a thing, when acted, then result",
               epic="EP0001", status="Draft"):
        d = root / "sdlc-studio" / "stories"; d.mkdir(parents=True, exist_ok=True)
        v = f"- **Verify:** {verify}\n" if verify else ""
        (d / f"US{num:04d}-x.md").write_text(
            f"# US{num:04d}: s\n\n> **Status:** {status}\n> **Epic:** [{epic}](../epics/{epic}-x.md)\n\n"
            f"## Acceptance Criteria\n\n### AC1\n- {ac_text}\n{v}", encoding="utf-8")

    def test_weak_verify_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, 1, verify="curl $API/x prints < 0.300")
            self.assertIn("weak-verify", _load().audit_unit(root, "US0001")["issues"])

    def test_executable_verify_not_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, 2, verify='jest "US0002 works"')
            self.assertNotIn("weak-verify", _load().audit_unit(root, "US0002")["issues"])

    def test_cross_epic_ac_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ed = root / "sdlc-studio" / "epics"; ed.mkdir(parents=True)
            (ed / "EP0001-x.md").write_text("# EP0001: authentication\n", encoding="utf-8")
            (ed / "EP0002-x.md").write_text("# EP0002: billing\n", encoding="utf-8")
            self._story(root, 1, ac_text="the billing total updates correctly", epic="EP0001")
            r = _load().audit_batch(root, ["US0001"])
            self.assertIn("cross-epic-ac", r["units"][0]["issues"])


if __name__ == "__main__":
    unittest.main()


class RegressionTestHeuristicTests(unittest.TestCase):
    """CR0128 heuristic 2: a Fixed/Done bug whose recorded tests have no integration/regression
    case is flagged. The check is a name-signal heuristic; proving the test hits the seams is a
    review judgement (the advisory boundary)."""

    def _bug_with(self, root, num, status, body_extra):
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        body = (f"# BG{num:04d}: b\n\n> **Status:** {status}\n> **Severity:** Medium\n\n"
                f"## Summary\n\nx\n\n## Steps to Reproduce\n\n1. do it\n\n"
                f"## Proposed Fix\n\ndo this\n{body_extra}\n")
        (d / f"BG{num:04d}-x.md").write_text(body, encoding="utf-8")
        return _load().audit_unit(root, f"BG{num:04d}")

    def test_fixed_bug_unit_test_only_is_flagged(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            r = self._bug_with(root, 1, "Fixed",
                               "\n## Tests\n\n- **Verify:** pytest tests/test_widget.py::test_parse\n")
            self.assertIn("missing-regression-test", r["issues"])

    def test_fixed_bug_with_regression_test_passes(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            r = self._bug_with(root, 2, "Fixed",
                               "\n## Tests\n\n- **Verify:** pytest tests/test_regression.py::test_dispatch_loop\n")
            self.assertNotIn("missing-regression-test", r["issues"])

    def test_fixed_bug_with_integration_test_passes(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            r = self._bug_with(root, 3, "Fixed",
                               "\n## Regression Test\n\nIntegration test at the router -> dispatcher seam.\n")
            self.assertNotIn("missing-regression-test", r["issues"])

    def test_open_bug_not_flagged(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            r = self._bug_with(root, 4, "Open",
                               "\n## Tests\n\n- **Verify:** pytest tests/test_widget.py::test_parse\n")
            self.assertNotIn("missing-regression-test", r["issues"])

    def test_fixed_bug_no_test_info_not_double_flagged(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            r = self._bug_with(root, 5, "Fixed", "")
            self.assertNotIn("missing-regression-test", r["issues"])
