"""Unit tests for scripts/lib/sdlc_md.py and the JSON guards that use it.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent


def _load(name: str, rel: str):
    """Load a module by file path (mirrors the sibling test modules)."""
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / rel)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sdlc_md = _load("sdlc_md", "lib/sdlc_md.py")
repo_map = _load("repo_map", "repo_map.py")
verify_ac = _load("verify_ac", "verify_ac.py")


class TimeTests(unittest.TestCase):
    def test_now_iso8601_shape(self) -> None:
        ts = sdlc_md.now_iso8601()
        self.assertRegex(ts, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

    def test_now_date_shape(self) -> None:
        self.assertRegex(sdlc_md.now_date(), r"^\d{4}-\d{2}-\d{2}$")


class JsonTests(unittest.TestCase):
    def test_loads_valid(self) -> None:
        self.assertEqual(sdlc_md.loads('{"a": 1}', None), {"a": 1})

    def test_loads_empty_and_blank_return_default(self) -> None:
        self.assertEqual(sdlc_md.loads("", []), [])
        self.assertEqual(sdlc_md.loads("   ", {}), {})

    def test_loads_malformed_returns_default(self) -> None:
        self.assertEqual(sdlc_md.loads("not json", "x"), "x")

    def test_read_json_missing_file(self) -> None:
        missing = Path(tempfile.gettempdir()) / "sdlc_md_no_such_file_42.json"
        self.assertEqual(sdlc_md.read_json(missing, {"d": 1}), {"d": 1})

    def test_read_json_valid_and_malformed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            good = Path(d) / "good.json"
            good.write_text('{"k": 2}', encoding="utf-8")
            self.assertEqual(sdlc_md.read_json(good, None), {"k": 2})
            bad = Path(d) / "bad.json"
            bad.write_text("{ broken", encoding="utf-8")
            self.assertIsNone(sdlc_md.read_json(bad, None))


class FieldTests(unittest.TestCase):
    SAMPLE = "# Add login\n\n> **Status:** In Progress\n> **Priority:** P1\n"

    def test_extract_field(self) -> None:
        self.assertEqual(sdlc_md.extract_field(self.SAMPLE, "Status"), "In Progress")
        self.assertEqual(sdlc_md.extract_field(self.SAMPLE, "Priority"), "P1")

    def test_extract_field_absent(self) -> None:
        self.assertIsNone(sdlc_md.extract_field(self.SAMPLE, "Owner"))

    def test_extract_h1_title(self) -> None:
        self.assertEqual(sdlc_md.extract_h1_title(self.SAMPLE), "Add login")
        self.assertIsNone(sdlc_md.extract_h1_title("no heading here"))

    def test_extract_record_id(self) -> None:
        self.assertEqual(sdlc_md.extract_record_id("US0001-login"), "US0001")
        self.assertEqual(sdlc_md.extract_record_id("CR-0001-add-auth"), "CR-0001")
        self.assertEqual(sdlc_md.extract_record_id("RFC-0007-design"), "RFC-0007")
        self.assertEqual(sdlc_md.extract_record_id("EP0042"), "EP0042")
        self.assertIsNone(sdlc_md.extract_record_id("readme"))

    def test_extract_ac_id(self) -> None:
        self.assertEqual(sdlc_md.extract_ac_id("### AC1: Happy path"), ("AC1", "Happy path"))
        self.assertEqual(sdlc_md.extract_ac_id("### AC12"), ("AC12", ""))
        self.assertIsNone(sdlc_md.extract_ac_id("## Not an AC"))


class SlugTests(unittest.TestCase):
    def test_slug(self) -> None:
        self.assertEqual(sdlc_md.slug("In Progress"), "in-progress")
        self.assertEqual(sdlc_md.slug("  Feature/Request!  "), "feature-request")


class WalkGlobTests(unittest.TestCase):
    def test_walk_glob_sorted_and_missing_dir(self) -> None:
        self.assertEqual(sdlc_md.walk_glob(Path("/no/such/dir/xyz"), "*.md"), [])
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            (base / "US0002-b.md").write_text("x", encoding="utf-8")
            (base / "US0001-a.md").write_text("x", encoding="utf-8")
            (base / "ignore.txt").write_text("x", encoding="utf-8")
            names = [p.name for p in sdlc_md.walk_glob(base, "US*.md")]
            self.assertEqual(names, ["US0001-a.md", "US0002-b.md"])


class JsonGuardRegressionTests(unittest.TestCase):
    """Closes the review gap: corrupt JSON must exit 2, not traceback."""

    def test_repo_map_query_exits_2_on_corrupt_map(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / "repo-map.json"
            bad.write_text("{ not json", encoding="utf-8")
            rc = repo_map.main(["query", "--map", str(bad), "--story", "login"])
            self.assertEqual(rc, 2)

    def test_verify_ac_report_exits_2_on_corrupt_report(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / "verify-report.json"
            bad.write_text("{ not json", encoding="utf-8")
            rc = verify_ac.main(["report", "--report", str(bad)])
            self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
