"""Determinism tests for review_prep staleness (CR0004) - RED first for the new behaviour."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parent.parent / "review_prep.py"


def _load():
    spec = importlib.util.spec_from_file_location("review_prep", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["review_prep"] = mod
    spec.loader.exec_module(mod)
    return mod


class ParseTests(unittest.TestCase):
    def test_z_and_offset_equal(self) -> None:
        mod = _load()
        self.assertEqual(mod._parse_dt("2026-06-20T12:00:00Z"),
                         mod._parse_dt("2026-06-20T12:00:00+00:00"))

    def test_naive_treated_as_utc(self) -> None:
        mod = _load()
        self.assertEqual(mod._parse_dt("2026-06-20T12:00:00"),
                         datetime(2026, 6, 20, 12, 0, tzinfo=timezone.utc))

    def test_unparseable_is_none(self) -> None:
        self.assertIsNone(_load()._parse_dt("not-a-date"))


class ModifiedTests(unittest.TestCase):
    def test_git_method_when_tracked(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                   "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
            run = lambda *a: subprocess.run(["git", "-C", str(root), *a], check=True,
                                            capture_output=True, env={**__import__("os").environ, **env})
            run("init", "-q")
            f = root / "prd.md"
            f.write_text("x", encoding="utf-8")
            run("add", "prd.md")
            run("commit", "-qm", "c")
            ts, method = mod._modified_iso(f, root)
            self.assertEqual(method, "git")
            self.assertIsNotNone(mod._parse_dt(ts))

    def test_mtime_fallback_when_untracked(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "prd.md"
            f.write_text("x", encoding="utf-8")
            _, method = mod._modified_iso(f, Path(d))  # not a git repo
            self.assertEqual(method, "mtime")

    def test_git_branch_verdict_flips(self) -> None:
        # Prove a needs_review verdict THROUGH the git branch (not the mtime path).
        import os
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                   "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
            run = lambda *a: subprocess.run(["git", "-C", str(root), *a], check=True,
                                            capture_output=True, env=env)
            run("init", "-q")
            base = root / "sdlc-studio"
            (base / ".local").mkdir(parents=True)
            (base / "prd.md").write_text("# prd\n", encoding="utf-8")
            run("add", "sdlc-studio/prd.md")
            run("commit", "-qm", "c")
            state = base / ".local" / "review-state.json"
            state.write_text(json.dumps({"artifacts": {"prd": {"last_reviewed": "2000-01-01T00:00:00Z"}}}), encoding="utf-8")
            self.assertTrue(mod.staleness(root)["prd"]["needs_review"])   # reviewed before commit
            state.write_text(json.dumps({"artifacts": {"prd": {"last_reviewed": "2999-01-01T00:00:00Z"}}}), encoding="utf-8")
            v = mod.staleness(root)["prd"]
            self.assertEqual(v["modified_method"], "git")
            self.assertFalse(v["needs_review"])                          # reviewed after commit


class MalformedTests(unittest.TestCase):
    def test_malformed_last_reviewed_warns_and_needs(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            base = root / "sdlc-studio"
            (base / ".local").mkdir(parents=True)
            (base / "prd.md").write_text("# prd\n", encoding="utf-8")
            (base / ".local" / "review-state.json").write_text(
                json.dumps({"artifacts": {"prd": {"last_reviewed": "garbage"}}}), encoding="utf-8")
            stale = mod.staleness(root)
            self.assertTrue(stale["prd"]["needs_review"])
            self.assertIn("warning", stale["prd"])
            self.assertEqual(stale["prd"]["modified_method"], "mtime")

    def test_warning_surfaced_in_prep_output(self) -> None:
        # AC3's contract: the malformed state is surfaced in the prep JSON, not
        # just the internal dict (kills a `"warnings": []` mutant).
        import io
        from contextlib import redirect_stdout
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            base = root / "sdlc-studio"
            (base / ".local").mkdir(parents=True)
            (base / "prd.md").write_text("# prd\n", encoding="utf-8")
            (base / ".local" / "review-state.json").write_text(
                json.dumps({"artifacts": {"prd": {"last_reviewed": "garbage"}}}), encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = mod.main(["prep", "--root", str(root), "--format", "json"])
            self.assertEqual(rc, 0)
            out = json.loads(buf.getvalue())
            self.assertTrue(any("prd" in w for w in out["warnings"]))


if __name__ == "__main__":
    unittest.main()
