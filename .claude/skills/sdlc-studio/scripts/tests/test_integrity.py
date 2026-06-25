"""Unit tests for integrity.py (RED first - the script does not exist yet)."""
from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "integrity.py"


def _load():
    spec = importlib.util.spec_from_file_location("integrity", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["integrity"] = mod
    spec.loader.exec_module(mod)
    return mod


def _epic(root, num=1, status="Ready"):
    d = root / "sdlc-studio" / "epics"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"EP{num:04d}-x.md").write_text(f"# EP{num:04d}: e\n\n> **Status:** {status}\n", encoding="utf-8")


def _story(root, num, status="Ready", epic="EP0001"):
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    body = f"# US{num:04d}: s\n\n> **Status:** {status}\n"
    if epic is not None:
        body += f"> **Epic:** [link](../epics/{epic}-x.md)\n"
    (d / f"US{num:04d}-x.md").write_text(body, encoding="utf-8")


def _bug(root, num, status="Fixed"):
    d = root / "sdlc-studio" / "bugs"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"BG{num:04d}-x.md").write_text(f"# BG{num:04d}: b\n\n> **Status:** {status}\n", encoding="utf-8")


class MissingTests(unittest.TestCase):
    def test_active_missing_epic_errors(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _epic(root, 1)
            _story(root, 1, epic="EP0001")   # well-formed
            _story(root, 2, epic=None)        # Ready, missing Epic -> error
            mod = _load()
            res = mod.detect_integrity(root)
            errs = [f for f in res["findings"] if f["severity"] == "error"]
            self.assertEqual(len(errs), 1)
            self.assertEqual(errs[0]["id"], "US0002")
            self.assertEqual(errs[0]["kind"], "missing-required")
            self.assertEqual(mod.main(["check", "--root", str(root)]), 1)

    def test_placeholder_epic_counts_as_missing(self) -> None:
        # `Epic: --` is an explicit no-link placeholder, not a real link.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _epic(root, 1)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True, exist_ok=True)
            (sd / "US0003-x.md").write_text(
                "# US0003: s\n\n> **Status:** Ready\n> **Epic:** --\n", encoding="utf-8")
            res = _load().detect_integrity(root)
            errs = [f for f in res["findings"] if f["severity"] == "error" and f["id"] == "US0003"]
            self.assertEqual(len(errs), 1)


class DanglingTests(unittest.TestCase):
    def test_valid_cross_type_reference_not_dangling(self) -> None:
        # Census must include all types: a story's Epic pointing at a real epic
        # is NOT dangling (locks census completeness; kills a "drop epics" mutant).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _epic(root, 1)
            _story(root, 1, epic="EP0001")
            res = _load().detect_integrity(root)
            self.assertEqual([f for f in res["findings"] if f["kind"] == "dangling"], [])
            self.assertEqual(res["summary"]["errors"], 0)

    def test_present_but_no_id_is_missing(self) -> None:
        # A required field that is non-blank but carries no resolvable ID is missing.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True, exist_ok=True)
            (sd / "US0005-x.md").write_text(
                "# US0005: s\n\n> **Status:** Ready\n> **Epic:** the authentication epic\n", encoding="utf-8")
            res = _load().detect_integrity(root)
            errs = [f for f in res["findings"] if f["severity"] == "error" and f["id"] == "US0005"]
            self.assertEqual(len(errs), 1)
            self.assertEqual(errs[0]["kind"], "missing-required")

    def test_dangling_advisory(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _epic(root, 1)
            _story(root, 1, epic="EP9099")    # required field present, ref does not resolve
            mod = _load()
            res = mod.detect_integrity(root)
            dang = [f for f in res["findings"] if f["kind"] == "dangling"]
            self.assertTrue(any(f["ref"] == "EP9099" for f in dang))
            self.assertTrue(all(f["severity"] == "advisory" for f in dang))
            self.assertEqual(mod.main(["check", "--root", str(root)]), 0)  # no errors


def _testspec(root, num, status="Draft", epic="EP0001", story=None):
    d = root / "sdlc-studio" / "test-specs"
    d.mkdir(parents=True, exist_ok=True)
    body = f"# TS{num:04d}: t\n\n> **Status:** {status}\n"
    if epic is not None:
        body += f"> **Epic:** [link](../epics/{epic}-x.md)\n"
    if story is not None:
        body += f"> **Story:** [link](../stories/{story}-x.md)\n"
    (d / f"TS{num:04d}-x.md").write_text(body, encoding="utf-8")


class TestSpecLinkTests(unittest.TestCase):
    def test_epic_scoped_testspec_no_story_passes(self) -> None:
        # An epic-scoped test-spec carries an Epic link but no single Story field
        # (reference-test-spec.md#epic-scoped-coverage). Story must not be required,
        # so this must not raise a missing-required error.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _epic(root, 1)
            _testspec(root, 5, status="Active", epic="EP0001", story=None)
            mod = _load()
            res = mod.detect_integrity(root)
            errs = [f for f in res["findings"] if f["severity"] == "error" and f["id"] == "TS0005"]
            self.assertEqual(errs, [])
            self.assertEqual(res["summary"]["errors"], 0)
            self.assertEqual(mod.main(["check", "--root", str(root)]), 0)

    def test_testspec_missing_epic_still_errors(self) -> None:
        # Epic stays required: an active test-spec with neither Epic nor Story
        # still flags a missing-required error on Epic.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _testspec(root, 6, status="Active", epic=None, story=None)
            mod = _load()
            res = mod.detect_integrity(root)
            errs = [f for f in res["findings"] if f["severity"] == "error" and f["id"] == "TS0006"]
            self.assertEqual(len(errs), 1)
            self.assertEqual(errs[0]["kind"], "missing-required")
            self.assertEqual(errs[0]["field"], "Epic")
            self.assertEqual(mod.main(["check", "--root", str(root)]), 1)

    def test_story_scoped_testspec_still_passes(self) -> None:
        # The other half of the scope contract (reference-test-spec.md, Story-level
        # row): a story-scoped test-spec with both Epic and a resolvable Story link
        # passes clean - no missing-required, no dangling. Guards against a fix that
        # over-corrects by ignoring test-specs, and locks that Epic still resolves
        # through the census for this type.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _epic(root, 1)
            _story(root, 7, epic="EP0001")
            _testspec(root, 7, status="Active", epic="EP0001", story="US0007")
            mod = _load()
            res = mod.detect_integrity(root)
            ts_findings = [f for f in res["findings"] if f["id"] == "TS0007"]
            self.assertEqual(ts_findings, [])
            self.assertEqual(res["summary"]["errors"], 0)
            self.assertEqual(mod.main(["check", "--root", str(root)]), 0)


class BugLinkTests(unittest.TestCase):
    def test_open_bug_missing_link_is_advisory(self) -> None:
        # A bug's Epic/Story link is recommended, not required: missing -> advisory
        # at any status (bugs are often filed pre-triage), never an error.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1, status="Open")   # active bug, no Epic/Story
            mod = _load()
            res = mod.detect_integrity(root)
            self.assertEqual(res["summary"]["errors"], 0)
            bug_findings = [f for f in res["findings"] if f["id"] == "BG0001"]
            self.assertTrue(bug_findings)
            self.assertTrue(all(f["severity"] == "advisory" for f in bug_findings))
            self.assertEqual(mod.main(["check", "--root", str(root)]), 0)

    def test_bug_dangling_reference_still_reported(self) -> None:
        # Optional links must not suppress a bug's DANGLING reference (guards a
        # future early-return-for-LINK_OPTIONAL mutant).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            dd = root / "sdlc-studio" / "bugs"
            dd.mkdir(parents=True, exist_ok=True)
            (dd / "BG0002-x.md").write_text(
                "# BG0002: b\n\n> **Status:** Open\n> **Epic:** EP9099\n", encoding="utf-8")
            res = _load().detect_integrity(root)
            dang = [f for f in res["findings"] if f["id"] == "BG0002" and f["kind"] == "dangling"]
            self.assertTrue(dang)
            self.assertTrue(all(f["severity"] == "advisory" for f in dang))
            self.assertEqual(res["summary"]["errors"], 0)


class GuidanceTests(unittest.TestCase):
    def test_guidance_printed(self) -> None:
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, epic=None)  # active story missing Epic -> missing-required
            buf = io.StringIO()
            with redirect_stdout(buf):
                _load().main(["check", "--root", str(root)])
            out = buf.getvalue()
            self.assertIn("Guidance:", out)
            self.assertIn("missing-required ->", out)


class TerminalTests(unittest.TestCase):
    def test_terminal_missing_is_advisory(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1, status="Fixed")     # terminal, missing Epic + Story
            mod = _load()
            res = mod.detect_integrity(root)
            self.assertTrue(res["findings"])
            self.assertTrue(all(f["severity"] == "advisory" for f in res["findings"]))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = mod.main(["check", "--root", str(root), "--format", "json"])
            self.assertEqual(rc, 0)
            self.assertIn("summary", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
