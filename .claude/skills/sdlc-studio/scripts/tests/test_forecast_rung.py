"""EP0151 / US0400: the forecast names its rung and reads UNMEASURED off the build rung."""
from __future__ import annotations

import importlib.util
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


class ForecastNamesItsRung(unittest.TestCase):
    """US0400: the forecast names the rung it prices; a non-build rung reads UNMEASURED."""

    def _root(self):
        d = Path(tempfile.mkdtemp(prefix="forecast_rung_"))
        (d / "sdlc-studio" / "stories").mkdir(parents=True)
        (d / "scripts").mkdir()
        (d / "scripts" / "repo_map.py").write_text("# marker\n")
        return d

    def _batch(self, d):
        f = d / "sdlc-studio" / "stories" / "US0001-x.md"
        f.write_text("# US0001: x\n\n> **Status:** Draft\n> **Points:** 5\n"
                     "> **Affects:** scripts/repo_map.py\n")
        return [{"id": "US0001", "path": str(f), "points": 5}]

    def test_design_rung_forecast_labels_the_rung(self) -> None:
        d = self._root()
        fc = sprint._token_forecast(d, self._batch(d), goal="design")
        self.assertEqual(fc["rung"], "design")

    def test_unmeasured_rung_rate_reads_unmeasured(self) -> None:
        d = self._root()
        fc = sprint._token_forecast(d, self._batch(d), goal="design")
        self.assertTrue(fc["rung_unmeasured"])
        self.assertEqual(fc["rate_source"], sprint.RATE_UNMEASURED_RUNG)
        # it must NOT borrow the build rate as this rung's measured rate
        self.assertNotIn(fc["rate_source"], (sprint.RATE_SEED, sprint.RATE_EVIDENCE,
                                             sprint.RATE_FIXED_FIT, sprint.RATE_VELOCITY))

    def test_unmeasured_rung_does_not_PRICE_the_marginal_only_relabels_it(self) -> None:
        # The defect the closing review caught: relabelling rate_source is not enough - the
        # marginal must not be SPENT. A design rung must not produce the build-rate number.
        d = self._root()
        design = sprint._token_forecast(d, self._batch(d), goal="design")
        done = sprint._token_forecast(d, self._batch(d), goal="done")
        self.assertTrue(design["marginal_unmeasured"])
        self.assertIsNone(design["rate"])                       # no per-point rate at all
        self.assertNotEqual(design["tokens"], done["tokens"])   # NOT the build number
        self.assertEqual(design["per_unit"]["US0001"], None)    # the unit is not priced
        self.assertGreater(done["tokens"], 0)                   # the build case is unregressed

    def test_build_rung_still_priced_and_named(self) -> None:
        d = self._root()
        fc = sprint._token_forecast(d, self._batch(d), goal="done")
        self.assertEqual(fc["rung"], "done")
        self.assertFalse(fc["rung_unmeasured"])
        # the honest build case still prices at a real measured/seed rate, unregressed
        self.assertNotEqual(fc["rate_source"], sprint.RATE_UNMEASURED_RUNG)
        self.assertGreater(fc["tokens"], 0)


if __name__ == "__main__":
    unittest.main()
