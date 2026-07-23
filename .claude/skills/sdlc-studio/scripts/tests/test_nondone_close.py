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
        # The run names the unit it delivered, as a real run does: the rung is read from the
        # run whose batch COVERS the retro, so a batch-less fixture describes no run at all.
        (d / "sdlc-studio" / ".local" / "run-state.json").write_text(
            json.dumps({"schema": 1, "run_id": "RUN-X", "goal": goal,
                        "outcome": "goal-reached", "batch": ["US0001"]}))
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

class RungBelongsToItsOwnRunTests(unittest.TestCase):
    """BG0272: the rung is a property of the run that DELIVERED the retro's units, not of
    whatever run happens to be open when the retro is re-read.

    `_run_rung` read the live run-state unconditionally, so re-running `retro accuracy` (or the
    sprint report) for an older retro after a new run opened re-stamped that retro with the NEW
    run's goal. A design run re-read under an open build run then published the 834,008/pt
    figure US0401 exists to withhold. The provenance is taken from the run record whose batch
    covers the retro's units - the live state or the archive - which is the same coverage rule
    the elapsed and token reads already obey.
    """

    def _proj(self, retro_batch="US0001", points=5):
        d = Path(tempfile.mkdtemp(prefix="run_rung_"))
        (d / "sdlc-studio" / ".local").mkdir(parents=True)
        (d / "sdlc-studio" / "retros").mkdir(parents=True)
        (d / "sdlc-studio" / "stories").mkdir(parents=True)
        for uid in [u.strip() for u in retro_batch.split(",")]:
            (d / "sdlc-studio" / "stories" / f"{uid}-x.md").write_text(
                f"# {uid}: x\n\n> **Status:** Done\n> **Points:** {points}\n")
        (d / "sdlc-studio" / "retros" / "RETRO0001-x.md").write_text(
            f"# RETRO-0001: x\n\n> **Batch:** {retro_batch}\n> **Delivered:** 1 / 1\n")
        return d

    def _live(self, d, run_id, goal, batch):
        (d / "sdlc-studio" / ".local" / "run-state.json").write_text(
            json.dumps({"schema": 1, "run_id": run_id, "goal": goal,
                        "outcome": "running", "batch": batch}))

    def _archived(self, d, run_id, goal, batch, started="2026-07-01T00:00:00Z"):
        arc = d / "sdlc-studio" / ".local" / "run-archive"
        arc.mkdir(parents=True, exist_ok=True)
        (arc / f"{run_id}.json").write_text(
            json.dumps({"schema": 1, "run_id": run_id, "goal": goal, "started_at": started,
                        "outcome": "goal-reached", "batch": batch}))

    def test_an_older_retro_reads_its_own_runs_rung_after_a_new_run_opened(self) -> None:
        d = self._proj()
        self._archived(d, "RUN-OLD", "design", ["US0001"])       # the run that delivered it
        self._live(d, "RUN-NEW", "done", ["US0002"])             # a later, unrelated build run
        res = retro.accuracy(d, "RETRO0001", sprint_tokens=2_500_000)
        self.assertEqual(res["batch"]["rung"], "design")
        # THE VALUE, not the label: the design rung withholds the rate, so re-reading an old
        # retro under a new build run must not resurrect a tokens-per-point for it
        self.assertIsNone(res["batch"]["sprint_tokens_per_point"])
        self.assertEqual(res["batch"]["sprint_actual_tokens"], 2_500_000)

    def test_the_live_run_supplies_the_rung_when_it_covers_the_retro(self) -> None:
        # The positive control: while its own run is still open, the retro reads that run.
        d = self._proj()
        self._live(d, "RUN-NOW", "design", ["US0001"])
        res = retro.accuracy(d, "RETRO0001", sprint_tokens=2_500_000)
        self.assertEqual(res["batch"]["rung"], "design")
        self.assertIsNone(res["batch"]["sprint_tokens_per_point"])

    def test_a_build_run_of_its_own_still_earns_its_rate(self) -> None:
        # ... and the archive lookup does not blanket-blank the honest build case.
        d = self._proj()
        self._archived(d, "RUN-OLD", "done", ["US0001"])
        self._live(d, "RUN-NEW", "design", ["US0002"])
        res = retro.accuracy(d, "RETRO0001", sprint_tokens=1_000_000)
        self.assertEqual(res["batch"]["rung"], "done")
        self.assertEqual(res["batch"]["sprint_tokens_per_point"],
                         retro._rate(1_000_000, res["batch"]["delivered_points"]))

    def test_the_newest_covering_run_wins_when_a_unit_was_redelivered(self) -> None:
        # A carried-over unit appears in two runs' batches. The retro belongs to the LATER
        # one that covers it, not to whichever archive file sorts first.
        d = self._proj(retro_batch="US0001, US0002")
        self._archived(d, "RUN-A", "design", ["US0001", "US0002"], "2026-07-01T00:00:00Z")
        self._archived(d, "RUN-B", "done", ["US0001", "US0002"], "2026-07-09T00:00:00Z")
        res = retro.accuracy(d, "RETRO0001", sprint_tokens=1_000_000)
        self.assertEqual(res["batch"]["rung"], "done")
        self.assertEqual(res["batch"]["sprint_tokens_per_point"],
                         retro._rate(1_000_000, res["batch"]["delivered_points"]))

    def test_no_run_covers_the_retro_and_the_build_default_holds(self) -> None:
        # An interactive sprint with no run record at all: the rung is unknown, and the
        # documented default is the build case rather than a blanked rate.
        d = self._proj()
        self._live(d, "RUN-NEW", "design", ["US0002"])   # covers nothing of this retro
        res = retro.accuracy(d, "RETRO0001", sprint_tokens=1_000_000)
        self.assertEqual(res["batch"]["rung"], "done")
        self.assertEqual(res["batch"]["sprint_tokens_per_point"],
                         retro._rate(1_000_000, res["batch"]["delivered_points"]))


if __name__ == "__main__":
    unittest.main()
