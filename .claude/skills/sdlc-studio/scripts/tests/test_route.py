"""Unit tests for route.py - difficulty-aware model-tier routing (RFC0026 / CR0189)."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

spec = importlib.util.spec_from_file_location("route", SCRIPTS / "route.py")
route = importlib.util.module_from_spec(spec)
sys.modules["route"] = route
spec.loader.exec_module(route)


def _story(tmp: Path, *, affects: str | None = None, points: str | None = None,
           acs: int = 0, name: str = "US0001-test-story.md") -> Path:
    """Write a minimal story with the requested signal fields present."""
    lines = ["# US0001: test story", "", "> **Status:** Ready"]
    if affects is not None:
        lines.append(f"> **Affects:** {affects}")
    if points is not None:
        lines.append(f"> **Story Points:** {points}")
    lines += ["", "## Acceptance Criteria", ""]
    for i in range(1, acs + 1):
        lines += [f"### AC{i}: thing {i}", f"- **Given** x{i}", ""]
    d = tmp / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    p = d / name
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def _code_file(tmp: Path, rel: str, complexity_blocks: int = 0) -> Path:
    """A Python file with `complexity_blocks` nested-if functions to raise cognitive score."""
    body = "def f(x):\n"
    body += "".join(f"    {'    ' * i}if x > {i}:\n" for i in range(complexity_blocks))
    body += f"    {'    ' * complexity_blocks}return x\n    return 0\n"
    p = tmp / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    return p


class EstimateTests(unittest.TestCase):
    def test_estimate_emits_full_shape(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            _code_file(tmp, "src/mod.py", complexity_blocks=3)
            story = _story(tmp, affects="src/mod.py", points="5", acs=3)
            est = route.estimate(tmp, story)
            for key in ("difficulty_score", "difficulty_band", "confidence",
                        "missing", "signals", "subscores"):
                self.assertIn(key, est)
            self.assertIsInstance(est["difficulty_score"], int)
            self.assertGreaterEqual(est["difficulty_score"], 0)
            self.assertLessEqual(est["difficulty_score"], 100)
            self.assertEqual(est["missing"], [])
            self.assertEqual(est["confidence"], "high")

    def test_estimate_missing_signals_default_half_not_zero(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            story = _story(tmp)  # no Affects, no points, no ACs
            est = route.estimate(tmp, story)
            # every subscore whose inputs did not resolve is 0.5, never 0
            for name in est["missing"]:
                self.assertEqual(est["subscores"][name], 0.5)
            self.assertGreaterEqual(len(est["missing"]), 2)
            self.assertEqual(est["confidence"], "low")
            self.assertEqual(est["difficulty_score"], 50)  # all-missing = exactly midline

    def test_estimate_new_files_raise_novelty(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            _code_file(tmp, "src/old.py", complexity_blocks=1)
            greenfield = _story(tmp, affects="src/old.py, src/brand_new.py", acs=3,
                                name="US0002-greenfield.md")
            existing = _story(tmp, affects="src/old.py", acs=3,
                              name="US0003-existing.md")
            e_green = route.estimate(tmp, greenfield)
            e_exist = route.estimate(tmp, existing)
            self.assertGreater(e_green["subscores"]["novel"],
                               e_exist["subscores"]["novel"])

    def test_bands_map_to_tiers(self) -> None:
        cfg = {}
        self.assertEqual(route.band_for(10, cfg), ("trivial", "tiny"))
        self.assertEqual(route.band_for(20, cfg), ("low", "small"))
        self.assertEqual(route.band_for(45, cfg), ("medium", "medium"))
        self.assertEqual(route.band_for(70, cfg), ("high", "large"))
        self.assertEqual(route.band_for(85, cfg), ("extreme", "xlarge"))


class DegradationTests(unittest.TestCase):
    def test_sparse_map_degrades_upward_only(self) -> None:
        models = {"small": "model-s", "large": "model-l"}
        self.assertEqual(route.resolve_tier("tiny", models), ("small", "model-s"))
        self.assertEqual(route.resolve_tier("small", models), ("small", "model-s"))
        self.assertEqual(route.resolve_tier("medium", models), ("large", "model-l"))
        self.assertEqual(route.resolve_tier("large", models), ("large", "model-l"))
        # nothing at/above xlarge declared -> largest declared
        self.assertEqual(route.resolve_tier("xlarge", models), ("large", "model-l"))

    def test_empty_map_yields_tier_name_with_null_model(self) -> None:
        self.assertEqual(route.resolve_tier("medium", {}), ("medium", None))


class PickTests(unittest.TestCase):
    def _routing_cfg(self, **over):
        cfg = {"enabled": True, "models": {t: f"m-{t}" for t in route.TIERS},
               "floor": {"bug": "small", "security": "medium"},
               "critic_tier": "match",
               "thresholds": {"tiny": 20, "small": 40, "medium": 60, "large": 80},
               "escalation": {"max_same_tier": 2}}
        cfg.update(over)
        return cfg

    def test_bug_kind_floor_lifts_trivial_to_small(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            bugs = tmp / "sdlc-studio" / "bugs"
            bugs.mkdir(parents=True)
            bug = bugs / "BG0001-tiny-bug.md"
            bug.write_text("# BG0001: tiny bug\n\n> **Status:** Open\n"
                           "> **Affects:** src/x.py\n", encoding="utf-8")
            _code_file(tmp, "src/x.py", complexity_blocks=0)
            picked = route.pick(tmp, bug, role="author", routing=self._routing_cfg())
            idx = route.TIERS.index(picked["tier"])
            self.assertGreaterEqual(idx, route.TIERS.index("small"))
            self.assertIn("floor:bug", picked["adjustments"])

    def test_low_confidence_bumps_one_tier_up(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            story = _story(tmp)  # everything missing -> low confidence, score 50 (medium)
            picked = route.pick(tmp, story, role="author", routing=self._routing_cfg())
            self.assertEqual(picked["tier"], "large")  # medium bumped up once
            self.assertIn("confidence:low", picked["adjustments"])

    def test_critic_matches_author_with_medium_floor_for_code(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            _code_file(tmp, "src/simple.py", complexity_blocks=0)
            story = _story(tmp, affects="src/simple.py", points="1", acs=1)
            author = route.pick(tmp, story, role="author", routing=self._routing_cfg())
            critic = route.pick(tmp, story, role="critic", routing=self._routing_cfg())
            # a trivially-scored CODE unit still gets a medium critic
            self.assertGreaterEqual(route.TIERS.index(critic["tier"]),
                                    route.TIERS.index("medium"))
            self.assertGreaterEqual(route.TIERS.index(critic["tier"]),
                                    route.TIERS.index(author["tier"]))

    def test_critic_above_lifts_one_tier(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            _code_file(tmp, "src/simple.py", complexity_blocks=0)
            story = _story(tmp, affects="src/simple.py", points="1", acs=1)
            match = route.pick(tmp, story, role="critic",
                               routing=self._routing_cfg(critic_tier="match"))
            above = route.pick(tmp, story, role="critic",
                               routing=self._routing_cfg(critic_tier="above"))
            self.assertGreaterEqual(route.TIERS.index(above["tier"]),
                                    route.TIERS.index(match["tier"]))

    def test_doc_only_unit_gets_no_medium_critic_floor(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            doc = tmp / "docs" / "guide.md"
            doc.parent.mkdir(parents=True)
            doc.write_text("# guide\n", encoding="utf-8")
            story = _story(tmp, affects="docs/guide.md", points="1", acs=1)
            critic = route.pick(tmp, story, role="critic", routing=self._routing_cfg())
            self.assertLess(route.TIERS.index(critic["tier"]),
                            route.TIERS.index("medium"))


class EscalateTests(unittest.TestCase):
    def test_escalate_steps_to_next_declared_tier(self) -> None:
        models = {"tiny": "a", "medium": "b", "xlarge": "c"}
        r = route.escalate_tier("tiny", models)
        self.assertEqual((r["tier"], r["model"]), ("medium", "b"))
        r = route.escalate_tier("medium", models)
        self.assertEqual((r["tier"], r["model"]), ("xlarge", "c"))

    def test_escalate_at_max_reports_at_max(self) -> None:
        models = {"tiny": "a", "medium": "b"}
        r = route.escalate_tier("medium", models)
        self.assertTrue(r["at_max"])

    def test_escalate_with_empty_map_walks_abstract_tiers(self) -> None:
        r = route.escalate_tier("small", {})
        self.assertEqual(r["tier"], "medium")
        self.assertIsNone(r["model"])


class CliTests(unittest.TestCase):
    def test_estimate_cli_json(self) -> None:
        import contextlib, io, json
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            _code_file(tmp, "src/mod.py", complexity_blocks=2)
            story = _story(tmp, affects="src/mod.py", points="3", acs=2)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = route.main(["estimate", "--unit", str(story),
                                 "--root", str(tmp), "--format", "json"])
            self.assertEqual(rc, 0)
            out = json.loads(buf.getvalue())
            self.assertIn("difficulty_score", out)

    def test_tiers_cli_resolves_map(self) -> None:
        import contextlib, io, json
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            (tmp / "sdlc-studio").mkdir(parents=True)
            (tmp / "sdlc-studio" / ".config.yaml").write_text(
                textwrap.dedent("""\
                    routing:
                      enabled: true
                      models:
                        small: model-s
                        large: model-l
                """), encoding="utf-8")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = route.main(["tiers", "--root", str(tmp), "--format", "json"])
            self.assertEqual(rc, 0)
            out = json.loads(buf.getvalue())
            self.assertEqual(out["tiny"], {"tier": "small", "model": "model-s"})
            self.assertEqual(out["xlarge"], {"tier": "large", "model": "model-l"})


if __name__ == "__main__":
    unittest.main()
