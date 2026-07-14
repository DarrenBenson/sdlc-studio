"""BG0140: the estimate-vs-actual evidence must survive a fresh clone.

The plan-time forecast is the AUTHORITATIVE record - the number a sprint is judged against,
and the only thing that makes the estimator falsifiable at all. It was written to
`sdlc-studio/.local/`, which is gitignored, so it was user-local runtime state on one machine:
on a fresh clone, on CI, or for any other person, every forecast was absent, every unit read
UNFORECAST, and the whole history read as no-evidence. The fix defeated itself.

These tests are repo-only (they assert facts about THIS project's recorded evidence), which is
why they live in `tools/tests/` and not in the shipped skill payload.

The load-bearing one is `FreshCloneReproducesTheRatio`: it builds a tree containing ONLY the
files git tracks - the index, so it holds whether or not the change has been committed yet -
and asserts the accuracy report still reproduces. If a fresh clone cannot reproduce the ratio,
it is not fixed.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"

#: The sprint this repo's own history is anchored on, and the numbers VELOCITY.md records for
#: it. Read off the committed velocity row, not recomputed - a test that recomputed them would
#: move with the code it is meant to be pinning.
RETRO = "RETRO0026"
UNITS = 5
RATIO = 0.39


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _git(*args: str, cwd: Path = REPO) -> str:
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True,
                          timeout=60, check=False).stdout


def _tracked_files() -> list[str]:
    """Everything git knows about, from the INDEX. A file that is staged but not yet committed
    is already tracked and would reach a clone on the next push; a file that is merely present
    in the working tree would not."""
    out = _git("ls-files", "-z")
    return [p for p in out.split("\0") if p]


class FreshCloneReproducesTheRatio(unittest.TestCase):
    """The whole bug, as one assertion. Copy only what git tracks into an empty tree - no
    `.local/`, nothing untracked - and run the public accuracy path against it."""

    @classmethod
    def setUpClass(cls) -> None:
        if not (REPO / ".git").exists():
            raise unittest.SkipTest("not a git checkout")
        if not list((REPO / "sdlc-studio" / "retros").glob(f"{RETRO}*.md")):
            raise unittest.SkipTest(f"{RETRO} is not present - nothing to reproduce")
        cls.tmp = tempfile.TemporaryDirectory()
        clone = Path(cls.tmp.name)
        for rel in _tracked_files():
            src = REPO / rel
            if not src.is_file():          # a deleted-but-still-indexed path
                continue
            dst = clone / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        cls.clone = clone
        cls.retro = _load("retro")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_the_clone_has_no_local_state_at_all(self) -> None:
        """The premise. If `.local/` came along, the test would prove nothing."""
        self.assertFalse((self.clone / "sdlc-studio" / ".local").exists(),
                         "the fresh-clone fixture is contaminated with runtime state")

    def test_every_unit_is_still_forecast_and_measured(self) -> None:
        res = self.retro.accuracy(str(self.clone), RETRO)
        self.assertTrue(res["ok"], res.get("errors"))
        self.assertEqual(res["n_units"], UNITS)
        self.assertEqual(res["n_forecast"], UNITS,
                         f"a fresh clone reads {res['unforecast']} as UNFORECAST - the "
                         f"plan-time forecast did not survive the clone, so the estimator "
                         f"cannot be falsified by anyone but the machine that ran the sprint")
        self.assertEqual(res["n_measured"], UNITS,
                         f"a fresh clone reads {res['unmeasured']} as UNMEASURED - the "
                         f"measured actuals did not survive the clone")

    def test_the_batch_ratio_reproduces(self) -> None:
        res = self.retro.accuracy(str(self.clone), RETRO)
        self.assertEqual(res["batch"]["ratio"], RATIO,
                         "the fresh clone does not reproduce the recorded batch ratio - the "
                         "evidence under VELOCITY.md is not in the repository")

    def test_the_committed_velocity_row_agrees_with_the_clone(self) -> None:
        """The derived record and the evidence under it must not have drifted apart."""
        rows = {r["id"]: r for r in self.retro.velocity_history(str(self.clone))}
        self.assertIn(RETRO, rows)
        res = self.retro.accuracy(str(self.clone), RETRO)
        self.assertEqual(rows[RETRO]["ratio"], res["batch"]["ratio"])
        self.assertEqual(rows[RETRO]["actual_tokens"], res["batch"]["actual_tokens"])
        self.assertEqual(rows[RETRO]["estimate"], res["batch"]["estimate"])


#: The 16 units that were actually MEASURED, as they read in the pre-migration log:
#: (unit, tokens, wall_time_s, model). Transcribed from the log before the move, so this
#: pins the evidence against what it was BEFORE the migration - value for value - rather
#: than against itself. They are three sprints of end-to-end instrumented runs and cannot
#: be re-measured; a migration that dropped one would be unrecoverable.
MEASURED = [
    ("BG0126", 46_792, 272, "claude-opus-4-8"),
    ("BG0127", 65_625, 347, "claude-opus-4-8"),
    ("BG0130", 42_687, 189, "claude-opus-4-8"),
    ("BG0132", 129_957, 725, "claude-opus-4-8"),
    ("BG0133", 217_139, 1431, "claude-opus-4-8"),
    ("BG0134", 71_935, 428, "claude-opus-4-8"),
    ("BG0135", 173_804, 1246, "claude-opus-4-8"),
    ("BG0136", 234_091, 1767, "claude-opus-4-8"),
    ("CR0248", 84_302, 485, "claude-opus-4-8"),
    ("CR0249", 98_513, 475, "claude-opus-4-8"),
    ("CR0250", 46_359, 80, "claude-opus-4-8"),
    ("CR0252", 205_534, 1134, "claude-opus-4-8"),
    ("CR0257", 97_863, 483, "claude-opus-4-8"),
    ("CR0258", 107_623, 690, "claude-opus-4-8"),
    ("CR0259", 144_711, 772, "claude-opus-4-8"),
    ("CR0260", 162_204, 1137, "claude-opus-4-8"),
]

#: The plan-time forecast recorded for each of them, and the estimator that produced it.
#: (unit, tokens, seed, TOKENS_PER_COGNITIVE). The two eras of the constant are both here on
#: purpose: the 5,000 era is what the 3.34x in-sample row was forecast by, and losing it would
#: erase the miss that caused the recalibration.
FORECAST = [
    ("BG0126", 245_000, 39, 5000), ("BG0127", 310_000, 52, 5000),
    ("BG0130", 125_000, 15, 5000), ("CR0248", 310_000, 52, 5000),
    ("CR0249", 245_000, 39, 5000), ("CR0250", 50_000, 0, 5000),
    ("CR0257", 67_400, 29, 600), ("CR0258", 77_000, 45, 600),
    ("BG0132", 73_400, 39, 600), ("CR0259", 67_400, 29, 600),
    ("CR0260", 67_400, 29, 600), ("CR0252", 80_000, 0, 600),
    ("BG0133", 63_800, 23, 600), ("BG0136", 73_400, 39, 600),
    ("BG0134", 50_000, 0, 600), ("BG0135", 81_200, 52, 600),
]


class TheMigratedEvidenceIsIntact(unittest.TestCase):
    """Attack the migration. A migration that silently drops a record is the worst possible
    outcome: these are the only measured runs the project has, and they cannot be re-measured.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.tel = _load("telemetry")

    def test_every_measured_actual_survives_with_its_values_unchanged(self) -> None:
        got = self.tel.actuals(str(REPO))
        for uid, tokens, wall, model in MEASURED:
            self.assertIn(uid, got, f"{uid} was lost in the migration")
            self.assertEqual(got[uid]["tokens"], tokens, uid)
            self.assertEqual(got[uid]["wall_time_s"], wall, uid)
            self.assertEqual(got[uid]["model"], model, uid)

    def test_the_evidence_base_only_ever_grows(self) -> None:
        """Every unit measured before the move is still measured after it. Later sprints add
        their own records - the log is alive - but nothing may leave it: a measured run cannot
        be re-measured, so a record that disappears is gone for good."""
        got = {uid for uid, rec in self.tel.actuals(str(REPO)).items() if rec.get("tokens")}
        lost = {uid for uid, *_ in MEASURED} - got
        self.assertEqual(lost, set(), f"measured units vanished from the evidence base: {lost}")

    def test_every_forecast_survives_with_its_constants(self) -> None:
        got = self.tel.forecasts(str(REPO))
        for uid, tokens, seed, tpc in FORECAST:
            self.assertIn(uid, got, f"the plan-time forecast for {uid} was lost")
            self.assertEqual(got[uid]["tokens"], tokens, uid)
            self.assertEqual(got[uid]["seed"], seed, uid)
            self.assertEqual(got[uid]["constants"]["TOKENS_PER_COGNITIVE"], tpc, uid)
            self.assertEqual(got[uid]["constants"]["BASE_TOKEN_BUDGET"], 50_000, uid)

    def test_the_evidence_is_tracked_by_git(self) -> None:
        """Not merely present - TRACKED. This is the entire bug."""
        tracked = set(_tracked_files())
        evidence = [p for p in tracked
                    if p.startswith("sdlc-studio/retros/evidence/") and p.endswith(".jsonl")]
        self.assertTrue(evidence, "no evidence log is tracked by git")
        self.assertFalse([p for p in tracked if "/.local/" in p],
                         "runtime state is tracked - the boundary was drawn wrong")

    def test_no_evidence_log_is_gitignored(self) -> None:
        for rel in sorted(p for p in _tracked_files()
                          if p.startswith("sdlc-studio/retros/evidence/")):
            ignored = subprocess.run(["git", "check-ignore", "-q", rel], cwd=str(REPO),
                                     capture_output=True, timeout=30, check=False)
            self.assertNotEqual(ignored.returncode, 0, f"{rel} is gitignored")


class TheThreeSprintsAllStillRate(unittest.TestCase):
    """Not just the anchor sprint. Every sprint the velocity history claims a ratio for must
    still be reproducible from the tracked evidence, or the history is quoting numbers nothing
    in the repository can back."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.retro = _load("retro")

    def test_every_rated_velocity_row_reproduces_from_the_tracked_evidence(self) -> None:
        rows = [r for r in self.retro.velocity_history(str(REPO)) if r["ratio"] is not None]
        self.assertGreaterEqual(len(rows), 3, "the three measured sprints are the evidence base")
        for row in rows:
            res = self.retro.accuracy(str(REPO), row["id"])
            self.assertEqual(res["batch"]["ratio"], row["ratio"], row["id"])
            self.assertEqual(res["n_forecast"], row["forecast"], row["id"])
            self.assertEqual(res["n_measured"], row["measured"], row["id"])


if __name__ == "__main__":
    unittest.main()
