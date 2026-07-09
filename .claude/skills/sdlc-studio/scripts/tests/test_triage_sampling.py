"""Unit tests for triage_sampling.py (US0066): the seeded human-sampling policy (AC1) and the
triage-quality metrics computed from the records (AC2).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, DIR / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


ts = _load("triage_sampling", "triage_sampling.py")


def _batch() -> list[dict]:
    """A Critical, a raiser/triager disagreement, and a pool of 10 agreed-Medium findings."""
    return [
        {"id": "BG0001", "severity": "Critical", "triage_severity": "Critical"},
        {"id": "BG0002", "severity": "Low", "triage_severity": "High"},  # disagreement
        *[{"id": f"BG01{i:02d}", "severity": "Medium", "triage_severity": "Medium"}
          for i in range(10)],
    ]


class SamplingPolicyTests(unittest.TestCase):
    """AC1: every Critical + every disagreement + the configured fraction of the rest."""

    def test_always_samples_critical_and_disagreement(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ids = {p["id"] for p in ts.sample(_batch(), root=d, seed=1)}
            self.assertIn("BG0001", ids)   # Critical
            self.assertIn("BG0002", ids)   # raiser Low vs triager High -> disagreement

    def test_samples_configured_fraction_of_the_rest(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            picked = ts.sample(_batch(), root=d, seed=1)
            pool = [p for p in picked if p["id"] not in ("BG0001", "BG0002")]
            self.assertEqual(len(pool), 2)   # round(10 * 0.20) = 2 of the agreed pool

    def test_deterministic_for_a_given_seed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            a = [p["id"] for p in ts.sample(_batch(), root=d, seed=7)]
            b = [p["id"] for p in ts.sample(_batch(), root=d, seed=7)]
            self.assertEqual(a, b)

    def test_seed_changes_the_pool_subset(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            variants = {frozenset(p["id"] for p in ts.sample(_batch(), root=d, seed=s))
                        for s in range(10)}
            # Critical + disagreement are always sampled; the agreed-pool pick is seed-driven,
            # so across a range of seeds more than one subset appears (not a constant choice).
            self.assertGreater(len(variants), 1)
            for v in variants:
                self.assertTrue({"BG0001", "BG0002"} <= v)  # always-sampled remain stable


def _finding(root: Path, type_: str, num: int, sev: str, tsev: str, status: str) -> None:
    dirs = {"bug": "bugs", "cr": "change-requests", "rfc": "rfcs"}
    prefix = {"bug": "BG", "cr": "CR", "rfc": "RFC"}[type_]
    d = root / "sdlc-studio" / dirs[type_]
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{prefix}{num:04d}-x.md").write_text(
        f"# {prefix}{num:04d}: x\n\n> **Status:** {status}\n> **Severity:** {sev}\n"
        f"> **Triage-severity:** {tsev}\n\n## Summary\n\ns\n", encoding="utf-8")


class TriageMetricsTests(unittest.TestCase):
    """AC2: metrics computed from the records - no hand-counting."""

    def test_metrics_false_positive_rate_from_records(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _finding(root, "bug", 1, "Medium", "Medium", "Won't Fix")  # triaged then invalid
            _finding(root, "bug", 2, "Medium", "Medium", "Fixed")       # triaged, valid
            _finding(root, "bug", 3, "High", "High", "Open")            # not terminal
            m = ts.metrics(root)
            self.assertEqual(m["triaged"], 3)
            self.assertEqual(m["terminal"], 2)
            self.assertEqual(m["invalid_closed"], 1)
            self.assertEqual(m["false_positive_rate"], 0.5)             # 1 of 2 terminal

    def test_metrics_severity_inflation_from_records(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _finding(root, "bug", 1, "Low", "High", "Open")     # triager inflated
            _finding(root, "bug", 2, "High", "Low", "Open")     # triager deflated
            _finding(root, "bug", 3, "Medium", "Medium", "Open")  # agreed
            si = ts.metrics(root)["severity_inflation"]
            self.assertEqual(si["inflated"], 1)
            self.assertEqual(si["deflated"], 1)

    def test_metrics_sampled_pending_audit(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _finding(root, "bug", 1, "Medium", "Medium", "Open")       # sampled, still open
            _finding(root, "bug", 2, "Medium", "Medium", "Fixed")      # sampled, concluded
            ts.record_sample(root, ["BG0001", "BG0002"])
            self.assertEqual(ts.metrics(root)["sampled_pending_audit"], ["BG0001"])

    def test_metrics_empty_on_v2_untriaged_project(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # a bug with no Triage-severity is not a triaged finding
            (root / "sdlc-studio" / "bugs").mkdir(parents=True)
            (root / "sdlc-studio" / "bugs" / "BG0001-x.md").write_text(
                "# BG0001: x\n\n> **Status:** Open\n> **Severity:** Low\n\n## Summary\n\ns\n",
                encoding="utf-8")
            m = ts.metrics(root)
            self.assertEqual(m["triaged"], 0)
            self.assertEqual(m["false_positive_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
