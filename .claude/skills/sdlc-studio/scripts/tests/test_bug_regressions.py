"""Regression tests for the bug-clearing sprint (BG0144, BG0146).

Kept in one isolated file so they do not collide with the concurrent fixture migration in
test_sprint.py / test_two_backlogs.py.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / filename)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sys.path.insert(0, str(_SCRIPTS))
sprint = _load("sprint", "sprint.py")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class AffectsResolveGroomingTests(unittest.TestCase):
    """BG0144: the grooming gate refuses a unit whose declared `Affects` paths ALL fail to
    resolve on disk (a fictional list) - while tolerating SOME unresolved paths (a file the unit
    will create), because a real change almost always touches at least one file that exists."""

    def _bug(self, root: Path, num: int, affects: str) -> dict:
        _write(root / "sdlc-studio" / "bugs" / f"BG{num:04d}-x.md",
               f"# BG{num:04d}: b\n\n> **Status:** Open\n> **Severity:** Medium\n"
               f"> **Affects:** {affects}\n> **Points:** 2\n")
        return {"id": f"BG{num:04d}", "type": "bug",
                "path": str(root / "sdlc-studio" / "bugs" / f"BG{num:04d}-x.md")}

    def test_all_fictional_affects_is_ungroomed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            unit = self._bug(root, 1, "src/does-not-exist.py")
            bd = sprint.breakdown(root, [unit])
            ids = {u["id"] for u in bd["ungroomed"]}
            self.assertIn("BG0001", ids)
            # the refusal names the unresolvable path so the author can fix the typo
            u = next(u for u in bd["ungroomed"] if u["id"] == "BG0001")
            self.assertIn("src/does-not-exist.py", u["unresolvable"])

    def test_one_real_path_grooms_even_with_a_greenfield_sibling(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            (root / "src").mkdir()
            (root / "src" / "real.py").write_text("", encoding="utf-8")   # exists
            # one real file, one the unit will CREATE (greenfield) - legitimately groomed
            unit = self._bug(root, 2, "src/real.py, src/new-file.py")
            bd = sprint.breakdown(root, [unit])
            self.assertIn("BG0002", bd["groomed"])
            self.assertNotIn("BG0002", {u["id"] for u in bd["ungroomed"]})


class SampleClassProvenanceTests(unittest.TestCase):
    """BG0146: a velocity row is IN-SAMPLE (training error) only when the constants that MADE its
    forecast are the ones its actuals were fitted to. A row forecast by an OLDER estimator, whose
    actuals were later folded into the current fit, judges the estimator that made it - a genuine
    out-of-sample falsification, never training error. So a recalibration cannot relabel the
    falsifications that justified it."""

    def test_fit_set_row_forecast_by_old_constants_is_stale_not_in_sample(self) -> None:
        # RETRO0025 is in CALIBRATION_FIT_RETROS, but was forecast by the RETIRED base/tpc
        # estimator - its ratio judges THAT estimator out-of-sample.
        old = {"BASE_TOKEN_BUDGET": 50000, "TOKENS_PER_COGNITIVE": 600}
        self.assertEqual(sprint.sample_class("RETRO0025", old, "."), sprint.SAMPLE_STALE)
        self.assertEqual(sprint.sample_class("RETRO0026", old, "."), sprint.SAMPLE_STALE)

    def test_fit_set_row_forecast_by_current_constants_is_in_sample(self) -> None:
        cur = sprint.forecast_constants(".")
        self.assertEqual(sprint.sample_class("RETRO0025", cur, "."), sprint.SAMPLE_IN)

    def test_non_fit_row_forecast_by_current_constants_is_out_of_sample(self) -> None:
        cur = sprint.forecast_constants(".")
        self.assertEqual(sprint.sample_class("RETRO0099", cur, "."), sprint.SAMPLE_OUT)

    def test_unforecast_row_is_none(self) -> None:
        self.assertEqual(sprint.sample_class("RETRO0025", None, "."), sprint.SAMPLE_NONE)


if __name__ == "__main__":
    unittest.main()
