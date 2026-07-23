"""EP0130 / US0371: a green-but-open unit is flagged built-not-closed and kept out of the
build forecast; an all-built batch is pointed at the close path, not a build."""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _load(name):
    spec = importlib.util.spec_from_file_location(
        name, Path(__file__).resolve().parent.parent / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sprint = _load("sprint")


class BuiltNotClosed(unittest.TestCase):
    """US0371: the plan tells built-not-closed from unbuilt so it prices work, not deliveries."""

    def _root(self):
        d = Path(tempfile.mkdtemp(prefix="built_not_closed_"))
        (d / "sdlc-studio" / "stories").mkdir(parents=True)
        (d / "sdlc-studio" / ".local").mkdir(parents=True)
        (d / "scripts").mkdir()
        (d / "scripts" / "repo_map.py").write_text("# marker\n")
        return d

    def _story(self, d, num, status="Draft"):
        f = d / "sdlc-studio" / "stories" / f"US{num:04d}-x.md"
        f.write_text(f"# US{num:04d}: x\n\n> **Status:** {status}\n> **Points:** 5\n"
                     "> **Affects:** scripts/repo_map.py\n")
        return {"id": f"US{num:04d}", "path": str(f), "points": 5}

    def _report(self, d, entries):
        (d / "sdlc-studio" / ".local" / "verify-report.json").write_text(
            json.dumps({"stories": entries}))

    def test_green_draft_flagged_not_forecast_as_new(self) -> None:
        d = self._root()
        batch = [self._story(d, 1), self._story(d, 2)]
        # US0001 all-green, US0002 unrun
        self._report(d, {"US0001-x": {"verified": 3, "failed": 0, "stale": 0}})
        fc = sprint._token_forecast(d, batch, goal="done")
        self.assertIn("US0001", fc["built_not_closed"])
        self.assertNotIn("US0001", fc["units"])        # not priced as new work
        self.assertNotIn("US0001", fc["per_unit"])
        self.assertEqual(fc["points"], 5)              # only US0002's points remain
        self.assertIn("US0002", fc["units"])
        self.assertFalse(fc["all_built"])              # a mixed batch is NOT all-built

    def test_unverified_draft_forecast_as_new(self) -> None:
        d = self._root()
        batch = [self._story(d, 1)]
        # failing / unrun -> NOT built-not-closed, priced normally
        self._report(d, {"US0001-x": {"verified": 2, "failed": 1, "stale": 0}})
        fc = sprint._token_forecast(d, batch, goal="done")
        self.assertNotIn("US0001", fc["built_not_closed"])
        self.assertIn("US0001", fc["units"])
        self.assertEqual(fc["points"], 5)

    def test_all_built_batch_points_at_close(self) -> None:
        d = self._root()
        batch = [self._story(d, 1), self._story(d, 2)]
        self._report(d, {"US0001-x": {"verified": 3, "failed": 0, "stale": 0},
                         "US0002-x": {"verified": 1, "failed": 0, "stale": 0}})
        fc = sprint._token_forecast(d, batch, goal="done")
        self.assertTrue(fc["all_built"])
        self.assertEqual(sorted(fc["built_not_closed"]), ["US0001", "US0002"])
        self.assertEqual(fc["points"], 0)


if __name__ == "__main__":
    unittest.main()
