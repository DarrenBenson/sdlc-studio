"""Unit tests for plan.py.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "plan.py"
_spec = importlib.util.spec_from_file_location("plan", SCRIPT_PATH)
assert _spec and _spec.loader
plan = importlib.util.module_from_spec(_spec)
sys.modules["plan"] = plan
_spec.loader.exec_module(plan)


def _make_plan(plans_dir: Path, slug: str, heading: str = "Plan - do the thing",
               age_days: int = 0, prefix: str = "") -> Path:
    plans_dir.mkdir(parents=True, exist_ok=True)
    path = plans_dir / f"{slug}.md"
    path.write_text(f"{prefix}# {heading}\n\nBody.\n", encoding="utf-8")
    if age_days:
        old = time.time() - age_days * 86400
        os.utime(path, (old, old))
    return path


def _run(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = plan.main(argv)
    return rc, out.getvalue(), err.getvalue()


class FirstHeadingTests(unittest.TestCase):
    def test_plain_heading(self) -> None:
        self.assertEqual(plan.first_heading("# Title\n\nBody\n"), "Title")

    def test_skips_yaml_frontmatter(self) -> None:
        text = "---\ntitle: x\n# not a heading\n---\n\n## Real Heading\n"
        self.assertEqual(plan.first_heading(text), "Real Heading")

    def test_skips_html_comment(self) -> None:
        text = "<!-- header\ncomment -->\n\n# After Comment\n"
        self.assertEqual(plan.first_heading(text), "After Comment")

    def test_no_heading(self) -> None:
        self.assertEqual(plan.first_heading("just prose\n"), "(no heading)")


class ListTests(unittest.TestCase):
    def test_list_happy_path(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            plans = Path(d)
            _make_plan(plans, "add-auth", heading="Plan - add auth")
            rc, out, _ = _run(["list", "--plans-dir", d])
            self.assertEqual(rc, 0)
            self.assertIn("add-auth", out)
            self.assertIn("Plan - add auth", out)
            self.assertIn("1 active plan(s)", out)

    def test_list_missing_dir_is_sane(self) -> None:
        rc, out, _ = _run(["list", "--plans-dir", "/tmp/does-not-exist-sdlc"])
        self.assertEqual(rc, 0)
        self.assertIn("No plans found", out)

    def test_list_excludes_archive_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            plans = Path(d)
            _make_plan(plans, "active-one")
            _make_plan(plans / "archive" / "2026-01", "old-one")
            rc, out, _ = _run(["list", "--plans-dir", d])
            self.assertEqual(rc, 0)
            self.assertNotIn("old-one", out)
            rc, out, _ = _run(["list", "--all", "--plans-dir", d])
            self.assertIn("old-one", out)
            self.assertIn("[archived]", out)

    def test_stale_filtering(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            plans = Path(d)
            _make_plan(plans, "fresh-plan", age_days=1)
            _make_plan(plans, "stale-plan", age_days=45)
            rc, out, _ = _run(["list", "--stale", "--plans-dir", d,
                               "--format", "json"])
            self.assertEqual(rc, 0)
            data = json.loads(out)
            self.assertEqual([p["slug"] for p in data["plans"]], ["stale-plan"])
            self.assertGreater(data["plans"][0]["age_days"], 30)

    def test_stale_threshold_override(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _make_plan(Path(d), "fairly-old", age_days=10)
            rc, out, _ = _run(["list", "--stale", "--days", "5",
                               "--plans-dir", d, "--format", "json"])
            self.assertEqual(rc, 0)
            self.assertEqual(json.loads(out)["count"], 1)

    def test_json_record_shape(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _make_plan(Path(d), "shape-check", heading="Plan - shapes")
            rc, out, _ = _run(["list", "--plans-dir", d, "--format", "json"])
            self.assertEqual(rc, 0)
            rec = json.loads(out)["plans"][0]
            self.assertEqual(rec["slug"], "shape-check")
            self.assertEqual(rec["heading"], "Plan - shapes")
            self.assertFalse(rec["archived"])
            self.assertIn("modified", rec)


class ArchiveTests(unittest.TestCase):
    def test_archive_happy_path(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            plans = Path(d)
            src = _make_plan(plans, "ship-it")
            rc, out, _ = _run(["archive", "ship-it", "--plans-dir", d])
            self.assertEqual(rc, 0)
            month = datetime.now(timezone.utc).strftime("%Y-%m")
            dest = plans / "archive" / month / "ship-it.md"
            self.assertTrue(dest.is_file())
            self.assertFalse(src.exists())
            self.assertIn("Archived ship-it", out)

    def test_archive_missing_slug_errors(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            rc, _, err = _run(["archive", "no-such-plan", "--plans-dir", d])
            self.assertEqual(rc, 1)
            self.assertIn("no active plan named 'no-such-plan'", err)

    def test_archive_already_archived_errors(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            plans = Path(d)
            _make_plan(plans / "archive" / "2026-02", "done-already")
            rc, _, err = _run(["archive", "done-already", "--plans-dir", d])
            self.assertEqual(rc, 1)
            self.assertIn("already archived", err)

    def test_archive_never_overwrites_existing_target(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            plans = Path(d)
            src = _make_plan(plans, "name-clash", heading="Active copy")
            month = datetime.now(timezone.utc).strftime("%Y-%m")
            existing = _make_plan(plans / "archive" / month, "name-clash",
                                  heading="Archived copy")
            rc, _, err = _run(["archive", "name-clash", "--plans-dir", d])
            self.assertEqual(rc, 1)
            self.assertIn("refusing to overwrite", err)
            self.assertTrue(src.exists())
            self.assertIn("Archived copy",
                          existing.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
