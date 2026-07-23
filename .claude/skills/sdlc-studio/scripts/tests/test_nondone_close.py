"""EP0151 / US0401: a non-done rung close records tokens with the rate left blank."""
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


retro = _load("retro")


class NonDoneCloseLeavesRateBlank(unittest.TestCase):
    """US0401: a design-rung row records tokens without a tokens-per-point rate; a done-rung
    row still computes one."""

    def _setup(self, goal):
        d = Path(tempfile.mkdtemp(prefix="nondone_close_"))
        (d / "sdlc-studio" / ".local").mkdir(parents=True)
        (d / "sdlc-studio" / "retros").mkdir(parents=True)
        (d / "sdlc-studio" / "stories").mkdir(parents=True)
        (d / "sdlc-studio" / ".local" / "run-state.json").write_text(
            json.dumps({"schema": 1, "run_id": "RUN-X", "goal": goal,
                        "outcome": "goal-reached", "batch": []}))
        # one delivered story carrying points, named individually in the retro Batch
        (d / "sdlc-studio" / "stories" / "US0001-x.md").write_text(
            "# US0001: x\n\n> **Status:** Done\n> **Points:** 5\n")
        (d / "sdlc-studio" / "retros" / "RETRO0001-x.md").write_text(
            "# RETRO-0001: x\n\n> **Batch:** US0001\n> **Delivered:** 1 / 1\n")
        return d

    def test_design_rung_records_tokens_without_rate(self) -> None:
        d = self._setup("design")
        res = retro.accuracy(d, "RETRO0001", sprint_tokens=2_500_000)
        self.assertEqual(res["batch"]["rung"], "design")
        # tokens recorded, rate BLANK - the 834,008/pt garbage never reaches the row
        self.assertEqual(res["batch"]["sprint_actual_tokens"], 2_500_000)
        self.assertIsNone(res["batch"]["sprint_tokens_per_point"])

    def test_done_rung_still_computes_rate(self) -> None:
        d = self._setup("done")
        res = retro.accuracy(d, "RETRO0001", sprint_tokens=1_000_000)
        self.assertEqual(res["batch"]["rung"], "done")
        # the build rung keeps its measurement
        self.assertEqual(res["batch"]["sprint_tokens_per_point"], retro._rate(1_000_000, res["batch"]["delivered_points"]))
        self.assertIsNotNone(res["batch"]["sprint_tokens_per_point"])

if __name__ == "__main__":
    unittest.main()
